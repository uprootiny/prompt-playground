"""
Tests for template system
"""

import pytest
from prompts.templates import (
    TEMPLATES,
    get_template,
    render_template,
    get_all_categories,
    PromptTemplate,
)


def test_templates_loaded():
    """Test that templates are loaded"""
    assert len(TEMPLATES) > 0
    assert "code_generation" in TEMPLATES


def test_template_structure():
    """Test template data structure"""
    template = TEMPLATES["code_generation"]
    assert isinstance(template, PromptTemplate)
    assert template.id == "code_generation"
    assert template.name
    assert template.template
    assert template.category
    assert isinstance(template.variables, list)


def test_get_template():
    """Test getting template by ID"""
    template = get_template("code_generation")
    assert template.id == "code_generation"


def test_get_template_not_found():
    """Test getting non-existent template"""
    with pytest.raises(ValueError):
        get_template("nonexistent")


def test_render_template_simple():
    """Test rendering a template"""
    template = get_template("code_generation")
    values = {
        "language": "Python",
        "task": "sort a list"
    }
    rendered = render_template(template, values)
    assert "Python" in rendered
    assert "sort a list" in rendered
    assert "{{" not in rendered  # No unrendered variables


def test_render_template_missing_variable():
    """Test rendering with missing variables"""
    template = get_template("code_generation")
    values = {
        "language": "Python"
        # Missing 'task'
    }
    with pytest.raises(ValueError):
        render_template(template, values)


def test_get_all_categories():
    """Test getting all categories"""
    categories = get_all_categories()
    assert isinstance(categories, list)
    assert "coding" in categories
    assert "creative" in categories
    assert len(categories) > 0


def test_all_templates_have_required_fields():
    """Test that all templates have required fields"""
    for template_id, template in TEMPLATES.items():
        assert template.id == template_id
        assert template.name
        assert template.template
        assert template.category
        assert isinstance(template.variables, list)
        assert isinstance(template.example_values, dict)


def test_all_templates_variables_match():
    """Test that template variables match placeholders"""
    for template in TEMPLATES.values():
        # Find all {{variable}} placeholders
        import re
        placeholders = re.findall(r'\{\{(\w+)\}\}', template.template)

        # All placeholders should be in variables list
        for placeholder in placeholders:
            assert placeholder in template.variables, \
                f"Template {template.id} has placeholder {{{{{placeholder}}}}} not in variables list"


def test_example_values_match_variables():
    """Test that example values match template variables"""
    for template in TEMPLATES.values():
        for variable in template.variables:
            assert variable in template.example_values, \
                f"Template {template.id} missing example value for variable '{variable}'"


def test_render_with_example_values():
    """Test rendering all templates with their example values"""
    for template in TEMPLATES.values():
        try:
            rendered = render_template(template, template.example_values)
            assert rendered
            assert "{{" not in rendered  # No unrendered variables
        except Exception as e:
            pytest.fail(f"Failed to render template {template.id} with example values: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
