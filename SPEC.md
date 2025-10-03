# Prompt Playground - Technical Specification

**Project**: Side-by-side LLM prompt comparison tool
**Timeline**: 1 week (parallel with LLM Safety deployment)
**Status**: Starting now
**Code Reuse**: 70% from LLM Safety Playground

---

## Executive Summary

Interactive tool for testing and comparing different prompt variations across multiple LLMs simultaneously. Shows response quality, cost, latency, and allows A/B testing of prompt engineering strategies.

**Key Value Props:**
- Side-by-side comparison (GPT-4 vs Claude vs GPT-3.5)
- Prompt template library
- Cost tracking per request
- Response time metrics
- Prompt variation testing (temperature, max_tokens, etc.)
- Save/share prompt configurations

---

## Architecture (Reusing LLM Safety)

```
Browser (Vanilla JS) → FastAPI Backend
                        ├─ LLM Providers (COPY from LLM Safety!)
                        │   ├─ OpenAI
                        │   └─ Anthropic
                        ├─ Prompt Templates (NEW)
                        ├─ Cost Calculator (NEW)
                        └─ Comparison Engine (NEW)
```

### What We Copy from LLM Safety:
- ✅ `backend/llm/providers.py` (100% reuse)
- ✅ `backend/config.py` (minor edits)
- ✅ `backend/middleware.py` (100% reuse)
- ✅ `backend/metrics.py` (100% reuse)
- ✅ `Dockerfile` (100% reuse)
- ✅ `docker-compose.yml` (edit service name)
- ✅ Frontend structure (edit for comparison UI)

### What's New:
- Prompt template library
- Multi-provider comparison
- Cost tracking
- Response diff visualization

---

## Features

### 1. Multi-Provider Comparison
Run same prompt across:
- OpenAI GPT-4
- OpenAI GPT-3.5-turbo
- Anthropic Claude 3.5 Sonnet
- Anthropic Claude 3 Haiku

**Side-by-side display**:
```
┌──────────────┬──────────────┬──────────────┐
│   GPT-4      │  Claude 3.5  │  GPT-3.5     │
│ $0.03        │ $0.015       │ $0.002       │
│ 2.3s         │ 1.8s         │ 0.9s         │
│ Response...  │ Response...  │ Response...  │
└──────────────┴──────────────┴──────────────┘
```

### 2. Prompt Templates
Pre-built templates:
- Code generation
- Data extraction
- Creative writing
- Analysis/summarization
- Translation
- Q&A

**Variables**: `{{topic}}`, `{{style}}`, `{{format}}`

### 3. Parameter Testing
Test variations:
- Temperature (0.0 - 2.0)
- Max tokens
- Top-p
- Frequency penalty
- Presence penalty

### 4. Cost Tracking
Real-time cost calculation:
- Input tokens × price
- Output tokens × price
- Total per request
- Running total

### 5. Response Comparison
- Character diff highlighting
- Response length comparison
- Sentiment analysis (optional)
- Quality scoring (optional)

---

## Technical Implementation

### Backend (Mostly Copied!)

**`backend/llm/providers.py`** - COPY EXACTLY from LLM Safety:
```python
# Already has OpenAI and Anthropic!
# Just use it as-is
```

**`backend/prompts/templates.py`** - NEW:
```python
TEMPLATES = {
    "code_generation": {
        "name": "Code Generation",
        "template": "Write a {{language}} function that {{task}}",
        "variables": ["language", "task"],
        "system_prompt": "You are an expert programmer.",
    },
    "data_extraction": {
        "name": "Data Extraction",
        "template": "Extract {{fields}} from: {{text}}",
        "variables": ["fields", "text"],
    },
    # ... more templates
}
```

**`backend/prompts/cost.py`** - NEW:
```python
PRICING = {
    "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
}

def calculate_cost(model, input_tokens, output_tokens):
    pricing = PRICING.get(model, {"input": 0, "output": 0})
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    return input_cost + output_cost
```

**`backend/main.py`** - Adapted from LLM Safety:
```python
@app.post("/api/compare")
async def compare_prompts(request: CompareRequest):
    """Run prompt across multiple providers"""
    results = []

    for provider_name in request.providers:
        start = time.time()
        provider = create_provider(provider_name, model=request.model)

        response = provider.generate(
            request.prompt,
            system_prompt=request.system_prompt
        )

        latency = time.time() - start
        cost = calculate_cost(...)

        results.append({
            "provider": provider_name,
            "response": response,
            "latency": latency,
            "cost": cost
        })

    return results
```

### Frontend (Adapted from LLM Safety)

**`frontend/index.html`** - Similar structure:
- Template selector (instead of attack selector)
- Multiple response panels (instead of single)
- Cost/latency display

**`frontend/css/styles.css`** - COPY + adapt grid layout

**`frontend/js/app.js`** - Similar API calls, different UI updates

---

## Development Plan (1 Week)

### Day 1: Copy & Setup (2 hours)
- [x] Create directory structure
- [ ] Copy files from LLM Safety
- [ ] Update imports and names
- [ ] Git init

### Day 2-3: Backend (4 hours)
- [ ] Prompt templates library
- [ ] Cost calculation
- [ ] Compare endpoint
- [ ] Tests

### Day 4-5: Frontend (4 hours)
- [ ] Template selector
- [ ] Multi-panel response display
- [ ] Cost/latency visualization
- [ ] Parameter controls

### Day 6: Polish (2 hours)
- [ ] Error handling
- [ ] Loading states
- [ ] Documentation

### Day 7: Deploy (1 hour)
- [ ] Docker build
- [ ] Railway deploy
- [ ] Test live

---

## API Endpoints

### POST /api/compare
Run prompt across multiple providers

**Request**:
```json
{
  "prompt": "Explain quantum computing",
  "providers": ["openai", "anthropic"],
  "models": {
    "openai": "gpt-4",
    "anthropic": "claude-3-5-sonnet"
  },
  "temperature": 0.7
}
```

**Response**:
```json
{
  "results": [
    {
      "provider": "openai",
      "model": "gpt-4",
      "response": "...",
      "latency": 2.3,
      "cost": 0.03,
      "tokens": {"input": 10, "output": 500}
    },
    {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet",
      "response": "...",
      "latency": 1.8,
      "cost": 0.015,
      "tokens": {"input": 10, "output": 500}
    }
  ]
}
```

### GET /api/templates
Get all prompt templates

### POST /api/templates
Save custom template

---

## Synergy with LLM Safety

| Component | LLM Safety | Prompt Playground | Reuse % |
|-----------|------------|-------------------|---------|
| LLM Providers | ✅ | Copy exactly | 100% |
| Config | ✅ | Minor edits | 90% |
| Middleware | ✅ | Copy exactly | 100% |
| Metrics | ✅ | Copy exactly | 100% |
| Docker | ✅ | Copy exactly | 100% |
| Frontend structure | ✅ | Adapt layout | 60% |
| CSS | ✅ | Adapt grid | 70% |

**Total reuse**: ~70% of codebase

---

## Differentiation from LLM Safety

| Feature | LLM Safety | Prompt Playground |
|---------|------------|-------------------|
| Focus | Security/filtering | Comparison/optimization |
| Primary Use | Test attacks | Test prompts |
| Output | Safety report | Response comparison |
| Audience | Security engineers | Prompt engineers |
| Demo Value | Security awareness | Prompt engineering |

**Together**: Show comprehensive LLM engineering skills

---

## Success Metrics

- [ ] 3+ providers supported
- [ ] 10+ prompt templates
- [ ] Accurate cost tracking
- [ ] <500ms backend overhead (excluding LLM)
- [ ] Live deployed
- [ ] Demo video

---

**Ready to build!** Start by copying files from LLM Safety.
