import pytest
import os
import csv
import io


@pytest.fixture
def client_with_test_data(client):
    # Backup original data path
    old_data_path = os.environ.get('MATTER_DATA_PATH')
    test_data_path = os.path.join(os.getcwd(), 'data', 'test_matter.csv')
    os.environ['MATTER_DATA_PATH'] = test_data_path
    
    # Create a test CSV
    with open(test_data_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Product', 'Type', 'MAC', 'Pairing Code', 'Description', 'QR'])
        writer.writeheader()
        writer.writerow({
            'Product': 'Test Device',
            'Type': 'Test Type',
            'MAC': 'AA:BB:CC:DD:EE:FF',
            'Pairing Code': '123-45-678',
            'Description': 'Test Desc',
            'QR': ''
        })

    yield client, test_data_path

    if os.path.exists(test_data_path):
        os.remove(test_data_path)
    # Restore environment variable
    if old_data_path:
        os.environ['MATTER_DATA_PATH'] = old_data_path
    else:
        if 'MATTER_DATA_PATH' in os.environ:
            del os.environ['MATTER_DATA_PATH']

def test_export(client_with_test_data):
    c, _ = client_with_test_data
    response = c.get('/matter/export')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert b'AA:BB:CC:DD:EE:FF' in response.data

def test_import(client_with_test_data):
    c, _ = client_with_test_data
    # Create a CSV to import
    csv_data = [
        ['Product', 'Type', 'MAC', 'Pairing Code', 'Description', 'QR'],
        ['New Device', 'Type 2', '11:22:33:44:55:66', '987-65-432', 'New Desc', ''],
        ['Duplicate Device', 'Type 1', 'AA:BB:CC:DD:EE:FF', '123-45-678', 'Existing', '']
    ]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(csv_data)
    
    data = {
        'file': (io.BytesIO(output.getvalue().encode('utf-8')), 'test.csv')
    }
    
    response = c.post('/matter/import', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success']
    assert json_data['added_count'] == 1 # Only one should be added due to de-duplication
    
    # Verify content
    response = c.get('/matter')
    data = response.get_json()
    macs = [item['MAC'] for item in data]
    assert '11:22:33:44:55:66' in macs
    assert 'AA:BB:CC:DD:EE:FF' in macs
    assert len(data) == 2
