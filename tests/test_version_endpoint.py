import pytest
from app import app, VERSION

def test_version_in_health(client):
    """Verify /health endpoint returns the correct version from pyproject.toml."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert 'version' in data
    assert data['version'] == VERSION
    # Ensure it's not the default 0.0.0 (unless that's what's in pyproject.toml)
    assert data['version'] != "0.0.0"

def test_version_in_template_context(client):
    """Verify version is injected into template context."""
    with app.test_request_context():
        from app import inject_metadata
        context = inject_metadata()
        assert 'version' in context
        assert context['version'] == VERSION

def test_version_in_navbar(client):
    """Verify version is displayed in the navbar on the index page."""
    response = client.get('/')
    assert response.status_code == 200
    # Navbar usually has vVERSION
    expected = f'v{VERSION}'.encode()
    assert expected in response.data

def test_version_in_data_attribute(client):
    """Verify version is in the body's data-version attribute for JS to use."""
    response = client.get('/')
    assert response.status_code == 200
    expected = f'data-version="{VERSION}"'.encode()
    assert expected in response.data
