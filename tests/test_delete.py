import pytest
import csv

test_data = ['id,Product,Type,MAC,Pairing Code,Description,QR',
             'abc12,Device1,Type1,11:22:33:44:55:66,123-456,Desc1,QR1',
             'def34,Device2,Type2,AA:BB:CC:DD:EE:FF,123-456,Desc2,QR2',
]

def test_delete_device_success(client, matter_data_path):
    temp_path = matter_data_path(test_data)

    # Delete Device1 by record id
    response = client.delete('/matter/abc12')
    assert response.status_code == 200
    assert response.get_json() == {"success": True}
    
    # Verify it's gone from the CSV
    with open(temp_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
        assert len(data) == 1
        assert data[0]['id'] == 'def34'

def test_delete_device_not_found(client, matter_data_path):
    temp_path = matter_data_path(test_data)

    # Try to delete non-existent device
    response = client.delete('/matter/zzzzz')
    assert response.status_code == 404
    assert "error" in response.get_json()
    
    # Verify CSV is unchanged
    with open(temp_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
        assert len(data) == 2
