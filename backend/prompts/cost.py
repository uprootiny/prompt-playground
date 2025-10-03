"""
LLM cost calculation and tracking
"""

from typing import Dict, Tuple
import tiktoken


# Pricing per 1K tokens (as of Oct 2025)
PRICING = {
    # OpenAI
    "gpt-4": {
        "input": 0.03,
        "output": 0.06,
        "context_window": 8192,
    },
    "gpt-4-32k": {
        "input": 0.06,
        "output": 0.12,
        "context_window": 32768,
    },
    "gpt-4-turbo-preview": {
        "input": 0.01,
        "output": 0.03,
        "context_window": 128000,
    },
    "gpt-3.5-turbo": {
        "input": 0.0005,
        "output": 0.0015,
        "context_window": 16385,
    },
    "gpt-3.5-turbo-16k": {
        "input": 0.003,
        "output": 0.004,
        "context_window": 16385,
    },

    # Anthropic
    "claude-3-opus": {
        "input": 0.015,
        "output": 0.075,
        "context_window": 200000,
    },
    "claude-3-5-sonnet-20241022": {
        "input": 0.003,
        "output": 0.015,
        "context_window": 200000,
    },
    "claude-3-sonnet": {
        "input": 0.003,
        "output": 0.015,
        "context_window": 200000,
    },
    "claude-3-haiku": {
        "input": 0.00025,
        "output": 0.00125,
        "context_window": 200000,
    },
}


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int
) -> float:
    """
    Calculate cost for LLM API call

    Args:
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Total cost in USD
    """
    pricing = PRICING.get(model)

    if not pricing:
        # Unknown model, return 0
        return 0.0

    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]

    return input_cost + output_cost


def estimate_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Estimate token count for text

    Args:
        text: Text to count tokens for
        model: Model name (affects tokenizer)

    Returns:
        Estimated token count
    """
    try:
        # Use tiktoken for OpenAI models
        if model.startswith("gpt"):
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        else:
            # Rough estimate for Claude: ~4 chars per token
            return len(text) // 4
    except Exception:
        # Fallback: rough estimate
        return len(text) // 4


def format_cost(cost: float) -> str:
    """
    Format cost for display

    Args:
        cost: Cost in USD

    Returns:
        Formatted string (e.g., "$0.03" or "$0.0003")
    """
    if cost == 0:
        return "$0.00"
    elif cost < 0.001:
        return f"${cost:.6f}"
    elif cost < 0.01:
        return f"${cost:.5f}"
    elif cost < 0.1:
        return f"${cost:.4f}"
    else:
        return f"${cost:.3f}"


def get_cost_breakdown(
    model: str,
    input_tokens: int,
    output_tokens: int
) -> Dict[str, any]:
    """
    Get detailed cost breakdown

    Args:
        model: Model name
        input_tokens: Input token count
        output_tokens: Output token count

    Returns:
        Dict with cost breakdown
    """
    pricing = PRICING.get(model, {"input": 0, "output": 0})

    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    total_cost = input_cost + output_cost

    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
        "input_price_per_1k": pricing["input"],
        "output_price_per_1k": pricing["output"],
        "formatted_cost": format_cost(total_cost),
    }


def compare_costs(
    prompt: str,
    response: str,
    models: list
) -> Dict[str, Dict]:
    """
    Compare costs across multiple models

    Args:
        prompt: Input prompt
        response: Expected response (for token estimation)
        models: List of model names

    Returns:
        Dict mapping model names to cost breakdowns
    """
    input_tokens = estimate_tokens(prompt)
    output_tokens = estimate_tokens(response)

    comparisons = {}
    for model in models:
        comparisons[model] = get_cost_breakdown(model, input_tokens, output_tokens)

    return comparisons


def get_cheapest_model(costs: Dict[str, Dict]) -> Tuple[str, float]:
    """
    Find cheapest model from cost comparison

    Args:
        costs: Dict from compare_costs()

    Returns:
        Tuple of (model_name, cost)
    """
    cheapest = min(costs.items(), key=lambda x: x[1]["total_cost"])
    return cheapest[0], cheapest[1]["total_cost"]


def get_pricing_info(model: str) -> Dict:
    """Get pricing information for a model"""
    return PRICING.get(model, {
        "input": 0,
        "output": 0,
        "context_window": 0,
    })
