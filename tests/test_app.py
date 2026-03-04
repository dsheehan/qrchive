from app import VERSION

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Matter Devices' in response.data
    assert b'<table' in response.data
    # Check if version is present in navbar
    expected_version = f'v{VERSION}'.encode()
    assert expected_version in response.data

def test_licenses_route(client):
    response = client.get('/licenses')
    assert response.status_code == 200
    assert b'Open Source Licenses' in response.data
    assert b'flask' in response.data.lower()
    assert b'bootstrap' in response.data.lower()

def test_matter_route(client):
    response = client.get('/matter')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['Product'] == 'Tapo S505D'

def test_health_route(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['version'] == VERSION
