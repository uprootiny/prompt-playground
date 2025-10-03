"""
FastAPI backend for Prompt Playground
Compare prompts across multiple LLM providers
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import logging
import time
from pathlib import Path
from dotenv import load_dotenv
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from config import settings
from middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware, limiter
from metrics import metrics
from llm.providers import create_provider
from prompts.templates import TEMPLATES, get_template, render_template, get_all_categories
from prompts.cost import calculate_cost, get_cost_breakdown, estimate_tokens

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Prompt Playground",
    description="Side-by-side LLM prompt comparison tool",
    version="1.0.0",
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: HTTPException(
    status_code=429,
    detail="Rate limit exceeded. Please try again later."
))
app.add_middleware(SlowAPIMiddleware)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models

class CompareRequest(BaseModel):
    """Request to compare prompt across providers"""
    prompt: str
    providers: List[str] = ["openai", "anthropic"]
    models: Optional[Dict[str, str]] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: Optional[str] = None


class ProviderResponse(BaseModel):
    """Response from a single provider"""
    provider: str
    model: str
    response: str
    latency: float
    cost: float
    input_tokens: int
    output_tokens: int
    error: Optional[str] = None


class CompareResponse(BaseModel):
    """Comparison results"""
    prompt: str
    results: List[ProviderResponse]
    total_cost: float
    fastest: str
    cheapest: str


class TemplateRequest(BaseModel):
    """Request to render a template"""
    template_id: str
    values: Dict[str, str]


class TemplateResponse(BaseModel):
    """Rendered template"""
    template_id: str
    name: str
    rendered_prompt: str
    system_prompt: str
    variables: List[str]


# Endpoints

@app.get("/api/")
async def root():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": "Prompt Playground",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "templates_available": len(TEMPLATES),
        "categories": get_all_categories(),
    }


@app.get("/metrics")
async def get_metrics():
    """Get application metrics"""
    return metrics.get_summary()


@app.get("/api/templates")
async def get_templates():
    """Get all available templates"""
    metrics.increment_request("templates")

    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "category": t.category,
            "variables": t.variables,
            "example_values": t.example_values,
        }
        for t in TEMPLATES.values()
    ]


@app.get("/api/templates/category/{category}")
async def get_templates_by_category(category: str):
    """Get templates by category"""
    templates = [t for t in TEMPLATES.values() if t.category == category]

    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "variables": t.variables,
        }
        for t in templates
    ]


@app.get("/api/templates/{template_id}")
async def get_template_by_id(template_id: str):
    """Get specific template"""
    try:
        template = get_template(template_id)
        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "template": template.template,
            "variables": template.variables,
            "system_prompt": template.system_prompt,
            "category": template.category,
            "example_values": template.example_values,
        }
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")


@app.post("/api/render", response_model=TemplateResponse)
async def render_template_endpoint(request: TemplateRequest):
    """Render a template with provided values"""
    try:
        template = get_template(request.template_id)
        rendered = render_template(template, request.values)

        return TemplateResponse(
            template_id=template.id,
            name=template.name,
            rendered_prompt=rendered,
            system_prompt=template.system_prompt,
            variables=template.variables,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/compare", response_model=CompareResponse)
@limiter.limit("20/minute")
async def compare_prompts(request: Request, compare_request: CompareRequest):
    """
    Compare prompt across multiple LLM providers
    """
    start_time = time.time()
    metrics.increment_request("compare")

    logger.info(f"Compare request: {len(compare_request.providers)} providers, prompt={compare_request.prompt[:50]}...")

    results = []
    total_cost = 0.0

    for provider_name in compare_request.providers:
        provider_start = time.time()

        try:
            # Get model name (use provided or default)
            model = None
            if compare_request.models and provider_name in compare_request.models:
                model = compare_request.models[provider_name]

            # Create provider
            logger.debug(f"Creating provider: {provider_name} (model={model})")
            provider = create_provider(
                provider_name,
                model=model,
                temperature=compare_request.temperature,
                max_tokens=compare_request.max_tokens,
            )

            # Generate response
            logger.info(f"Generating with {provider.get_model_name()}")
            response_text = provider.generate(
                compare_request.prompt,
                system_prompt=compare_request.system_prompt,
            )

            latency = time.time() - provider_start

            # Estimate tokens and cost
            input_tokens = estimate_tokens(compare_request.prompt, provider.get_model_name())
            output_tokens = estimate_tokens(response_text, provider.get_model_name())
            cost = calculate_cost(provider.get_model_name(), input_tokens, output_tokens)
            total_cost += cost

            logger.debug(f"{provider_name} complete: {latency:.2f}s, ${cost:.4f}")

            results.append(ProviderResponse(
                provider=provider_name,
                model=provider.get_model_name(),
                response=response_text,
                latency=latency,
                cost=cost,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            ))

        except Exception as e:
            logger.error(f"Error with {provider_name}: {str(e)}", exc_info=True)
            metrics.record_error("llm")

            results.append(ProviderResponse(
                provider=provider_name,
                model=model or "unknown",
                response="",
                latency=time.time() - provider_start,
                cost=0.0,
                input_tokens=0,
                output_tokens=0,
                error=str(e),
            ))

    # Find fastest and cheapest
    successful_results = [r for r in results if not r.error]

    fastest = "none"
    cheapest = "none"

    if successful_results:
        fastest = min(successful_results, key=lambda r: r.latency).provider
        cheapest = min(successful_results, key=lambda r: r.cost).provider

    total_time = time.time() - start_time
    metrics.record_response_time(total_time)

    logger.info(f"Compare complete: {len(results)} results, ${total_cost:.4f}, {total_time:.2f}s")

    return CompareResponse(
        prompt=compare_request.prompt,
        results=results,
        total_cost=total_cost,
        fastest=fastest,
        cheapest=cheapest,
    )


@app.get("/api/pricing")
async def get_pricing():
    """Get pricing information for all models"""
    from prompts.cost import PRICING

    return {
        model: {
            "input_per_1k": info["input"],
            "output_per_1k": info["output"],
            "context_window": info["context_window"],
        }
        for model, info in PRICING.items()
    }


@app.get("/api/categories")
async def get_categories():
    """Get all template categories"""
    return get_all_categories()


# Serve frontend static files
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

    @app.get("/")
    async def serve_frontend():
        """Serve frontend HTML"""
        return FileResponse(str(frontend_path / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
