import pytest
import os
import csv
import tempfile

@pytest.fixture
def client_with_data(client):
    # Create a temporary CSV file
    fd, temp_path = tempfile.mkstemp(suffix='.csv')
    os.close(fd)
    
    # Set up some initial data
    headers = ['Product', 'Type', 'MAC', 'Pairing Code', 'Description', 'QR']
    initial_data = [
        {'Product': 'Device1', 'Type': 'Type1', 'MAC': '11:22:33:44:55:66', 'Pairing Code': '123-456', 'Description': 'Desc1', 'QR': 'QR1'},
        {'Product': 'Device2', 'Type': 'Type2', 'MAC': 'AA:BB:CC:DD:EE:FF', 'Pairing Code': '789-012', 'Description': 'Desc2', 'QR': 'QR2'}
    ]
    
    with open(temp_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(initial_data)
    
    # Override the data path
    old_data_path = os.environ.get('MATTER_DATA_PATH')
    os.environ['MATTER_DATA_PATH'] = temp_path

    yield client, temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)
    if old_data_path:
        os.environ['MATTER_DATA_PATH'] = old_data_path
    else:
        if 'MATTER_DATA_PATH' in os.environ:
            del os.environ['MATTER_DATA_PATH']

def test_delete_device_success(client_with_data):
    c, temp_path = client_with_data
    # Delete Device1
    mac_to_delete = '11:22:33:44:55:66'
    response = c.delete(f'/matter/{mac_to_delete}')
    assert response.status_code == 200
    assert response.get_json() == {"success": True}
    
    # Verify it's gone from the CSV
    with open(temp_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
        assert len(data) == 1
        assert data[0]['MAC'] == 'AA:BB:CC:DD:EE:FF'

def test_delete_device_not_found(client_with_data):
    c, temp_path = client_with_data
    # Try to delete non-existent device
    mac_to_delete = '00:00:00:00:00:00'
    response = c.delete(f'/matter/{mac_to_delete}')
    assert response.status_code == 404
    assert "error" in response.get_json()
    
    # Verify CSV is unchanged
    with open(temp_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
        assert len(data) == 2
