from conftest import _write

test_data = [
    'id,Product,Type,MAC,Pairing Code,Description,QR',
    'aaa11,Test Device,Test Type,AA:BB:CC:DD:EE:FF,123-45-678,Test Desc,',
]

csv_data = [
    'Product,Type,MAC,Pairing Code,Description,QR',
    'New Device,Type 2,11:22:33:44:55:66,987-65-432,New Desc,',
    'Another Device,Type 1,BB:CC:DD:EE:FF:00,123-45-678,Another,'
]


def test_export(client, matter_data_path):
    matter_data_path(test_data)

    response = client.get('/matter/export')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert b'AA:BB:CC:DD:EE:FF' in response.data

def test_import(client, matter_data_path):
    matter_data_path(test_data)
    temp_csv_file = _write(csv_data)

    with open(temp_csv_file, 'rb') as csv_file:
        data = {
            'file': (csv_file, 'test.csv')
        }

        response = client.post('/matter/import', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success']
    assert json_data['added_count'] == 2  # Both records imported (no MAC dedup)

    # Verify content
    response = client.get('/matter')
    data = response.get_json()
    macs = [item['MAC'] for item in data]
    assert '11:22:33:44:55:66' in macs
    assert 'AA:BB:CC:DD:EE:FF' in macs
    assert len(data) == 3
