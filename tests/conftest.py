import pytest
import os
import tempfile
from app import app

@pytest.fixture
def client():
    # Setup: use a temporary file for the data
    fd, temp_path = tempfile.mkstemp(suffix='.csv')
    os.close(fd)
    
    # Pre-populate with test data
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write("Product,Type,MAC,Pairing Code,Description,QR\n")
        f.write("Tapo S505D,Switch,00:11:22:33:44:55,12345678901,Bedroom Switch,test-qr-data\n")

    # Set environment variable so app uses this file
    old_path = os.getenv('MATTER_DATA_PATH')
    os.environ['MATTER_DATA_PATH'] = temp_path
    
    app.testing = True
    with app.test_client() as client:
        yield client

    # Teardown
    if old_path is None:
        del os.environ['MATTER_DATA_PATH']
    else:
        os.environ['MATTER_DATA_PATH'] = old_path
    
    if os.path.exists(temp_path):
        os.remove(temp_path)
