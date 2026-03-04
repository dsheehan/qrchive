import pytest

def test_qr_code_layout_requirement():
    with open('src/static/js/matter.js', 'r') as f:
        content = f.read()
    
    # Check for the correct bit shifts based on the new layout
    assert '<< 3n' in content   # Discriminator
    assert '<< 15n' in content  # Passcode
    assert '<< 42n' in content  # Flow
    assert '<< 44n' in content  # Capabilities
    assert '<< 52n' in content  # Vendor ID
    assert '<< 68n' in content  # Product ID

def test_manual_code_parsing():
    # Check if the JS has the logic to handle dashes
    with open('src/static/js/matter.js', 'r') as f:
        content = f.read()
    assert '.replace(/-/g, "")' in content
