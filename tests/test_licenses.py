from licenses import get_licenses_data

def test_get_licenses_data_python_packages():
    """Test that get_licenses_data correctly discovers and parses installed Python packages"""
    licenses = get_licenses_data()
    
    # Check if we have any Python licenses
    python_licenses = [l for l in licenses if l['type'] == 'Python']
    
    # Print for debugging
    print(f"Found {len(python_licenses)} Python licenses")
    for l in python_licenses[:5]:
        print(f"  {l['name']} ({l['version']}) - {l['license']}")
    
    # We expect 'flask' and 'pytest' to be there as they are in pyproject.toml
    python_names = [l['name'].lower() for l in python_licenses]
    assert 'flask' in python_names
    assert 'pytest' in python_names
    
    # We should at least verify that some have licenses
    with_license = [l for l in python_licenses if l['license'] != "Unknown"]
    print(f"Found {len(with_license)} packages with licenses")
    assert len(with_license) > 0, "No Python packages have license names"
    
    # Check for URLs
    with_url = [l for l in python_licenses if l['url']]
    print(f"Found {len(with_url)} packages with URLs")
    assert len(with_url) > 0, "No Python packages have URLs"
    
    # Specifically check Flask URL and License URL
    flask_entry = next((l for l in python_licenses if l['name'].lower() == 'flask'), None)
    if flask_entry:
        print(f"Flask URL: {flask_entry['url']}")
        print(f"Flask License URL: {flask_entry['license_url']}")
        assert flask_entry['url'], "Flask should have a URL"
        assert 'github.com' in flask_entry['url'].lower() or 'flask.palletsprojects.com' in flask_entry['url'].lower()
        
        assert flask_entry['license_url'], "Flask should have a license URL"
        assert 'github.com' in flask_entry['license_url'].lower() or 'flask.palletsprojects.com' in flask_entry['license_url'].lower()

def test_get_licenses_data_with_package_json():
    """Test that get_licenses_data correctly parses the package.json"""
    licenses = get_licenses_data()
    
    # Check if we have any JS/CSS licenses
    js_licenses = [l for l in licenses if l['type'] == 'JS/CSS']
    
    # Print for debugging
    print(f"Found {len(js_licenses)} JS/CSS licenses")
    for l in js_licenses:
        print(f"  {l['name']} ({l['version']}) - {l['license']}")
        
    assert len(js_licenses) >= 5, "Expected at least 5 JS/CSS licenses from package.json"
    
    # Verify a specific one
    bootstrap = next((l for l in js_licenses if l['name'] == 'bootstrap'), None)
    assert bootstrap is not None, "Bootstrap not found in JS/CSS licenses"
    assert bootstrap['license'] == 'MIT'
    assert 'github.com/twbs/bootstrap' in bootstrap['url']
    assert 'github.com/twbs/bootstrap/blob/main/LICENSE' in bootstrap['license_url']
    
    fontawesome = next((l for l in js_licenses if 'fontawesome' in l['name']), None)
    assert fontawesome is not None
    assert 'LICENSE.txt' in fontawesome['license_url']
