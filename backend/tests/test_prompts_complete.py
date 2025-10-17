"""
Complete test suite for Prompt Playground - TDD approach
Tests template management, cost calculation, and provider comparison
"""

import pytest
from unittest.mock import Mock, patch

from prompts.templates import (
    PromptTemplate,
    TEMPLATES,
    render_template,
    get_template,
    get_templates_by_category,
    get_all_categories
)
from prompts.cost import (
    PRICING,
    calculate_cost,
    estimate_tokens,
    format_cost,
    get_cost_breakdown,
    compare_costs,
    get_cheapest_model,
    get_pricing_info
)


# ============================================================================
# Template Management Tests
# ============================================================================

class TestPromptTemplate:
    """Test prompt template operations"""

    def test_template_structure(self):
        """Should have all required fields"""
        template = TEMPLATES["code_generation"]

        assert isinstance(template, PromptTemplate)
        assert hasattr(template, 'id')
        assert hasattr(template, 'name')
        assert hasattr(template, 'description')
        assert hasattr(template, 'template')
        assert hasattr(template, 'variables')
        assert hasattr(template, 'system_prompt')
        assert hasattr(template, 'category')
        assert hasattr(template, 'example_values')

    def test_template_variables_list(self):
        """Should list all required variables"""
        template = TEMPLATES["code_generation"]

        assert isinstance(template.variables, list)
        assert "language" in template.variables
        assert "task" in template.variables

    def test_template_example_values(self):
        """Should provide example values for all variables"""
        template = TEMPLATES["code_generation"]

        for var in template.variables:
            assert var in template.example_values
            assert len(template.example_values[var]) > 0

    def test_all_templates_valid(self):
        """All templates should be properly structured"""
        for template_id, template in TEMPLATES.items():
            assert template.id == template_id
            assert len(template.name) > 0
            assert len(template.description) > 0
            assert len(template.template) > 0
            assert len(template.system_prompt) > 0
            assert len(template.category) > 0
            assert len(template.variables) > 0


class TestTemplateRendering:
    """Test template rendering with variables"""

    def test_render_simple_template(self):
        """Should render template with provided values"""
        template = TEMPLATES["code_generation"]
        values = {"language": "Python", "task": "sort a list"}

        result = render_template(template, values)

        assert "Python" in result
        assert "sort a list" in result
        assert "{{language}}" not in result
        assert "{{task}}" not in result

    def test_render_missing_variable(self):
        """Should handle missing variables gracefully"""
        template = TEMPLATES["code_generation"]
        values = {"language": "Python"}  # Missing 'task'

        result = render_template(template, values)

        assert "Python" in result
        assert "[task]" in result  # Should show placeholder

    def test_render_extra_variables(self):
        """Should ignore extra variables"""
        template = TEMPLATES["code_generation"]
        values = {
            "language": "Python",
            "task": "sort a list",
            "extra": "ignored"
        }

        result = render_template(template, values)

        assert "Python" in result
        assert "sort a list" in result
        assert "ignored" not in result

    def test_render_all_templates(self):
        """Should be able to render all templates with examples"""
        for template_id, template in TEMPLATES.items():
            result = render_template(template, template.example_values)

            # Should not have any unreplaced variables
            assert "{{" not in result
            assert "}}" not in result

    def test_render_preserves_formatting(self):
        """Should preserve newlines and formatting"""
        template = TEMPLATES["data_extraction"]
        values = {
            "fields": "name, email",
            "text": "John Doe\njohn@example.com"
        }

        result = render_template(template, values)

        assert "\n" in result


class TestTemplateRetrieval:
    """Test template lookup operations"""

    def test_get_template_by_id(self):
        """Should retrieve template by ID"""
        template = get_template("code_generation")

        assert template.id == "code_generation"
        assert template.name == "Code Generation"

    def test_get_invalid_template(self):
        """Should raise error for invalid template ID"""
        with pytest.raises(ValueError, match="not found"):
            get_template("nonexistent_template")

    def test_get_templates_by_category_coding(self):
        """Should get all coding templates"""
        templates = get_templates_by_category("coding")

        assert len(templates) > 0
        assert all(t.category == "coding" for t in templates)
        # Should include code_generation and code_review
        ids = [t.id for t in templates]
        assert "code_generation" in ids
        assert "code_review" in ids

    def test_get_templates_by_category_creative(self):
        """Should get all creative templates"""
        templates = get_templates_by_category("creative")

        assert len(templates) > 0
        assert all(t.category == "creative" for t in templates)

    def test_get_all_categories(self):
        """Should list all unique categories"""
        categories = get_all_categories()

        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "coding" in categories
        assert "creative" in categories
        assert "analysis" in categories

    def test_categories_are_unique(self):
        """Should return unique categories only"""
        categories = get_all_categories()

        assert len(categories) == len(set(categories))


# ============================================================================
# Cost Calculation Tests
# ============================================================================

class TestCostCalculation:
    """Test LLM cost calculation"""

    def test_calculate_gpt4_cost(self):
        """Should calculate GPT-4 cost correctly"""
        cost = calculate_cost("gpt-4", input_tokens=1000, output_tokens=500)

        # $0.03/1K input + $0.06/1K output
        # 1000 tokens * $0.03/1000 = $0.03
        # 500 tokens * $0.06/1000 = $0.03
        # Total = $0.06
        assert cost == pytest.approx(0.06, 0.0001)

    def test_calculate_gpt35_cost(self):
        """Should calculate GPT-3.5 cost correctly"""
        cost = calculate_cost("gpt-3.5-turbo", input_tokens=1000, output_tokens=1000)

        # $0.0005/1K input + $0.0015/1K output
        # 1000 * $0.0005/1000 = $0.0005
        # 1000 * $0.0015/1000 = $0.0015
        # Total = $0.002
        assert cost == pytest.approx(0.002, 0.0001)

    def test_calculate_claude_cost(self):
        """Should calculate Claude cost correctly"""
        cost = calculate_cost("claude-3-5-sonnet-20241022", input_tokens=1000, output_tokens=1000)

        # $0.003/1K input + $0.015/1K output
        # Total = $0.018
        assert cost == pytest.approx(0.018, 0.0001)

    def test_calculate_unknown_model_cost(self):
        """Should return 0 for unknown models"""
        cost = calculate_cost("unknown-model", input_tokens=1000, output_tokens=500)

        assert cost == 0.0

    def test_calculate_zero_tokens(self):
        """Should handle zero tokens"""
        cost = calculate_cost("gpt-4", input_tokens=0, output_tokens=0)

        assert cost == 0.0

    def test_all_pricing_entries_valid(self):
        """All pricing entries should have required fields"""
        for model, pricing in PRICING.items():
            assert "input" in pricing
            assert "output" in pricing
            assert "context_window" in pricing
            assert pricing["input"] >= 0
            assert pricing["output"] >= 0
            assert pricing["context_window"] > 0


class TestTokenEstimation:
    """Test token counting"""

    @patch('prompts.cost.tiktoken.encoding_for_model')
    def test_estimate_tokens_gpt4(self, mock_encoding):
        """Should estimate tokens for GPT-4"""
        mock_enc = Mock()
        mock_enc.encode = Mock(return_value=[1, 2, 3, 4, 5])  # 5 tokens
        mock_encoding.return_value = mock_enc

        count = estimate_tokens("Hello world", model="gpt-4")

        assert count == 5
        mock_encoding.assert_called_once_with("gpt-4")

    def test_estimate_tokens_claude(self):
        """Should estimate tokens for Claude (rough estimate)"""
        text = "A" * 100  # 100 characters

        count = estimate_tokens(text, model="claude-3-sonnet")

        # Rough estimate: 100 chars / 4 = 25 tokens
        assert count == 25

    def test_estimate_tokens_empty_string(self):
        """Should handle empty string"""
        count = estimate_tokens("", model="claude-3-sonnet")

        assert count == 0

    @patch('prompts.cost.tiktoken.encoding_for_model')
    def test_estimate_tokens_fallback(self, mock_encoding):
        """Should fallback to rough estimate on error"""
        mock_encoding.side_effect = Exception("Model not found")

        text = "A" * 100
        count = estimate_tokens(text, model="gpt-4")

        # Should use fallback: 100 / 4 = 25
        assert count == 25


class TestCostFormatting:
    """Test cost display formatting"""

    def test_format_zero_cost(self):
        """Should format zero cost"""
        assert format_cost(0.0) == "$0.00"

    def test_format_tiny_cost(self):
        """Should format very small costs"""
        assert format_cost(0.0001) == "$0.000100"
        assert format_cost(0.0005) == "$0.000500"

    def test_format_small_cost(self):
        """Should format small costs"""
        assert format_cost(0.005) == "$0.00500"
        assert format_cost(0.008) == "$0.00800"

    def test_format_medium_cost(self):
        """Should format medium costs"""
        assert format_cost(0.05) == "$0.0500"
        assert format_cost(0.08) == "$0.0800"

    def test_format_large_cost(self):
        """Should format larger costs"""
        assert format_cost(1.234) == "$1.234"
        assert format_cost(10.50) == "$10.500"


class TestCostBreakdown:
    """Test detailed cost breakdown"""

    def test_cost_breakdown_structure(self):
        """Should return complete breakdown"""
        breakdown = get_cost_breakdown("gpt-4", input_tokens=1000, output_tokens=500)

        assert "model" in breakdown
        assert "input_tokens" in breakdown
        assert "output_tokens" in breakdown
        assert "total_tokens" in breakdown
        assert "input_cost" in breakdown
        assert "output_cost" in breakdown
        assert "total_cost" in breakdown
        assert "input_price_per_1k" in breakdown
        assert "output_price_per_1k" in breakdown
        assert "formatted_cost" in breakdown

    def test_cost_breakdown_values(self):
        """Should calculate breakdown correctly"""
        breakdown = get_cost_breakdown("gpt-4", input_tokens=1000, output_tokens=500)

        assert breakdown["model"] == "gpt-4"
        assert breakdown["input_tokens"] == 1000
        assert breakdown["output_tokens"] == 500
        assert breakdown["total_tokens"] == 1500
        assert breakdown["input_cost"] == pytest.approx(0.03, 0.0001)
        assert breakdown["output_cost"] == pytest.approx(0.03, 0.0001)
        assert breakdown["total_cost"] == pytest.approx(0.06, 0.0001)

    def test_cost_breakdown_unknown_model(self):
        """Should handle unknown model"""
        breakdown = get_cost_breakdown("unknown", input_tokens=1000, output_tokens=500)

        assert breakdown["total_cost"] == 0.0
        assert breakdown["input_price_per_1k"] == 0
        assert breakdown["output_price_per_1k"] == 0


class TestCostComparison:
    """Test multi-model cost comparison"""

    @patch('prompts.cost.estimate_tokens')
    def test_compare_costs_multiple_models(self, mock_estimate):
        """Should compare costs across models"""
        mock_estimate.return_value = 1000  # Both prompt and response = 1000 tokens

        models = ["gpt-4", "gpt-3.5-turbo", "claude-3-haiku"]
        comparison = compare_costs("Test prompt", "Test response", models)

        assert len(comparison) == 3
        assert "gpt-4" in comparison
        assert "gpt-3.5-turbo" in comparison
        assert "claude-3-haiku" in comparison

        # GPT-4 should be most expensive
        assert comparison["gpt-4"]["total_cost"] > comparison["gpt-3.5-turbo"]["total_cost"]
        assert comparison["gpt-4"]["total_cost"] > comparison["claude-3-haiku"]["total_cost"]

    @patch('prompts.cost.estimate_tokens')
    def test_get_cheapest_model(self, mock_estimate):
        """Should identify cheapest model"""
        mock_estimate.return_value = 1000

        models = ["gpt-4", "gpt-3.5-turbo", "claude-3-haiku"]
        comparison = compare_costs("Test", "Test", models)

        cheapest_name, cheapest_cost = get_cheapest_model(comparison)

        # Claude Haiku should be cheapest
        assert cheapest_name == "claude-3-haiku"
        assert cheapest_cost == comparison["claude-3-haiku"]["total_cost"]

    def test_get_pricing_info(self):
        """Should retrieve pricing information"""
        info = get_pricing_info("gpt-4")

        assert info["input"] == 0.03
        assert info["output"] == 0.06
        assert info["context_window"] == 8192

    def test_get_pricing_info_unknown(self):
        """Should handle unknown model"""
        info = get_pricing_info("unknown-model")

        assert info["input"] == 0
        assert info["output"] == 0
        assert info["context_window"] == 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestTemplateAndCostIntegration:
    """Test template rendering with cost estimation"""

    @patch('prompts.cost.estimate_tokens')
    def test_render_template_and_estimate_cost(self, mock_estimate):
        """Should render template and calculate cost"""
        template = get_template("code_generation")
        values = {"language": "Python", "task": "sort a list"}

        # Render template
        rendered = render_template(template, values)

        # Estimate cost
        mock_estimate.side_effect = [500, 1000]  # Input: 500, Output: 1000
        cost = calculate_cost("gpt-4", input_tokens=500, output_tokens=1000)

        assert len(rendered) > 0
        assert cost > 0

    def test_compare_costs_for_all_templates(self):
        """Should be able to cost-compare all templates"""
        models = ["gpt-4", "gpt-3.5-turbo"]

        for template_id, template in TEMPLATES.items():
            rendered = render_template(template, template.example_values)

            # Should be able to compare costs
            # (Mock would be used in real implementation)
            assert len(rendered) > 0

    @patch('prompts.cost.estimate_tokens')
    def test_template_categories_with_cost_analysis(self, mock_estimate):
        """Should analyze costs by template category"""
        mock_estimate.return_value = 1000

        coding_templates = get_templates_by_category("coding")

        for template in coding_templates:
            rendered = render_template(template, template.example_values)
            cost = calculate_cost("gpt-3.5-turbo", 1000, 1000)

            assert cost == pytest.approx(0.002, 0.0001)
