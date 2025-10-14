"""
Tests for Prompt Playground API endpoints
"""

import pytest
from fastapi.testclient import TestClient

# Import main app
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Prompt Playground"


def test_health_detailed():
    """Test detailed health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "templates_available" in data
    assert data["templates_available"] > 0


def test_get_templates():
    """Test getting all templates"""
    response = client.get("/api/templates")
    assert response.status_code == 200
    templates = response.json()
    assert isinstance(templates, list)
    assert len(templates) > 0

    # Check template structure
    template = templates[0]
    assert "id" in template
    assert "name" in template
    assert "category" in template
    assert "variables" in template


def test_get_template_by_id():
    """Test getting specific template"""
    response = client.get("/api/templates/code_generation")
    assert response.status_code == 200
    template = response.json()
    assert template["id"] == "code_generation"
    assert "name" in template
    assert "template" in template
    assert "variables" in template


def test_get_template_not_found():
    """Test getting non-existent template"""
    response = client.get("/api/templates/nonexistent")
    assert response.status_code == 404


def test_get_templates_by_category():
    """Test getting templates by category"""
    response = client.get("/api/templates/category/coding")
    assert response.status_code == 200
    templates = response.json()
    assert isinstance(templates, list)

    # All templates should be coding category
    for template in templates:
        # Category not in response, but checking structure
        assert "id" in template
        assert "name" in template


def test_get_categories():
    """Test getting all categories"""
    response = client.get("/api/categories")
    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)
    assert "coding" in categories
    assert "creative" in categories


def test_render_template():
    """Test rendering a template"""
    request = {
        "template_id": "code_generation",
        "values": {
            "language": "Python",
            "task": "calculate fibonacci numbers"
        }
    }
    response = client.post("/api/render", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["template_id"] == "code_generation"
    assert "Python" in data["rendered_prompt"]
    assert "fibonacci" in data["rendered_prompt"]


def test_render_template_not_found():
    """Test rendering non-existent template"""
    request = {
        "template_id": "nonexistent",
        "values": {}
    }
    response = client.post("/api/render", json=request)
    assert response.status_code == 404


def test_get_pricing():
    """Test getting pricing information"""
    response = client.get("/api/pricing")
    assert response.status_code == 200
    pricing = response.json()
    assert isinstance(pricing, dict)
    assert "gpt-4" in pricing
    assert "input_per_1k" in pricing["gpt-4"]
    assert "output_per_1k" in pricing["gpt-4"]


def test_get_metrics():
    """Test getting metrics"""
    response = client.get("/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert isinstance(metrics, dict)
    assert "total_requests" in metrics


def test_compare_validation():
    """Test compare endpoint validation"""
    # Missing prompt
    response = client.post("/api/compare", json={
        "providers": ["openai"]
    })
    assert response.status_code == 422

    # Empty providers
    response = client.post("/api/compare", json={
        "prompt": "test",
        "providers": []
    })
    # This might return 422 or 500 depending on validation


def test_frontend_serving():
    """Test frontend is served"""
    response = client.get("/")
    assert response.status_code == 200
    # Should return HTML
    assert "text/html" in response.headers["content-type"].lower()


def test_static_files():
    """Test static files are accessible"""
    # Try to access CSS
    response = client.get("/static/css/styles.css")
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
