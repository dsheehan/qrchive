def test_matter_table_is_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Matter Devices' in response.data
    assert b'<table' in response.data
    assert b'Tapo S505D' in response.data # Check if data from CSV is present

def test_matter_table_has_qr_column(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'data-header="QR"' in response.data
    assert b'Show QR' in response.data
