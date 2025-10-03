"""
Tests for cost calculation
"""

import pytest
from prompts.cost import (
    PRICING,
    calculate_cost,
    estimate_tokens,
    get_cost_breakdown,
)


def test_pricing_data():
    """Test pricing data structure"""
    assert "gpt-4" in PRICING
    assert "claude-3-5-sonnet-20241022" in PRICING

    for model, pricing in PRICING.items():
        assert "input" in pricing
        assert "output" in pricing
        assert "context_window" in pricing
        assert pricing["input"] > 0
        assert pricing["output"] > 0
        assert pricing["context_window"] > 0


def test_calculate_cost_gpt4():
    """Test cost calculation for GPT-4"""
    # 1000 input tokens, 500 output tokens
    cost = calculate_cost("gpt-4", 1000, 500)
    expected = (1000 / 1000 * 0.03) + (500 / 1000 * 0.06)
    assert cost == pytest.approx(expected, rel=0.01)


def test_calculate_cost_claude():
    """Test cost calculation for Claude"""
    cost = calculate_cost("claude-3-5-sonnet-20241022", 1000, 500)
    expected = (1000 / 1000 * 0.003) + (500 / 1000 * 0.015)
    assert cost == pytest.approx(expected, rel=0.01)


def test_calculate_cost_gpt35():
    """Test cost calculation for GPT-3.5"""
    cost = calculate_cost("gpt-3.5-turbo", 1000, 500)
    expected = (1000 / 1000 * 0.0005) + (500 / 1000 * 0.0015)
    assert cost == pytest.approx(expected, rel=0.01)


def test_calculate_cost_unknown_model():
    """Test cost calculation for unknown model defaults to GPT-4"""
    cost = calculate_cost("unknown-model", 1000, 500)
    # Should default to gpt-4 pricing
    expected = calculate_cost("gpt-4", 1000, 500)
    assert cost == expected


def test_estimate_tokens():
    """Test token estimation"""
    text = "This is a test sentence with some words."
    tokens = estimate_tokens(text)
    assert tokens > 0
    # Rough estimate: ~1 token per 4 characters
    assert tokens < len(text)


def test_estimate_tokens_empty():
    """Test token estimation with empty string"""
    tokens = estimate_tokens("")
    assert tokens == 0


def test_estimate_tokens_long():
    """Test token estimation with long text"""
    text = "word " * 1000
    tokens = estimate_tokens(text)
    assert tokens > 100
    assert tokens < 2000


def test_get_cost_breakdown():
    """Test cost breakdown"""
    breakdown = get_cost_breakdown("gpt-4", 1000, 500)

    assert "model" in breakdown
    assert "input_tokens" in breakdown
    assert "output_tokens" in breakdown
    assert "input_cost" in breakdown
    assert "output_cost" in breakdown
    assert "total_cost" in breakdown

    assert breakdown["model"] == "gpt-4"
    assert breakdown["input_tokens"] == 1000
    assert breakdown["output_tokens"] == 500
    assert breakdown["total_cost"] > 0


def test_cost_comparison():
    """Test that GPT-4 is more expensive than GPT-3.5"""
    gpt4_cost = calculate_cost("gpt-4", 1000, 1000)
    gpt35_cost = calculate_cost("gpt-3.5-turbo", 1000, 1000)
    assert gpt4_cost > gpt35_cost


def test_output_more_expensive_than_input():
    """Test that output tokens are more expensive than input"""
    # For most models, output is 2x input cost
    for model in ["gpt-4", "gpt-3.5-turbo"]:
        pricing = PRICING[model]
        assert pricing["output"] >= pricing["input"]


def test_all_models_have_pricing():
    """Test that all expected models have pricing"""
    expected_models = [
        "gpt-4",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
    ]

    for model in expected_models:
        assert model in PRICING, f"Missing pricing for {model}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
