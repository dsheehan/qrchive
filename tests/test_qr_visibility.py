import re


def test_qr_column_toggle_is_unchecked_by_default(client):
    response = client.get('/')
    assert response.status_code == 200

    content = response.data.decode('utf-8')

    # Find all column toggles: pairs of (input tag, label text)
    pairs = re.findall(r'(<input[^>]+id="col-toggle-\d+"[^>]*>)\s*<label[^>]*>([^<]+)</label>', content)
    assert pairs, "Could not find any column toggle pairs"

    toggle_map = {}
    for input_tag, label in pairs:
        toggle_map[label.strip()] = input_tag

    assert 'QR' in toggle_map, "Could not find QR column toggle"
    assert 'checked' not in toggle_map['QR'], "QR column toggle should not be checked by default"


def test_id_column_toggle_is_unchecked_by_default(client):
    response = client.get('/')
    assert response.status_code == 200

    content = response.data.decode('utf-8')

    pairs = re.findall(r'(<input[^>]+id="col-toggle-\d+"[^>]*>)\s*<label[^>]*>([^<]+)</label>', content)
    toggle_map = {label.strip(): tag for tag, label in pairs}

    assert 'id' in toggle_map, "Could not find id column toggle"
    assert 'checked' not in toggle_map['id'], "id column toggle should not be checked by default"


def test_product_column_toggle_is_checked_by_default(client):
    response = client.get('/')
    assert response.status_code == 200

    content = response.data.decode('utf-8')

    pairs = re.findall(r'(<input[^>]+id="col-toggle-\d+"[^>]*>)\s*<label[^>]*>([^<]+)</label>', content)
    toggle_map = {label.strip(): tag for tag, label in pairs}

    assert 'Product' in toggle_map, "Could not find Product column toggle"
    assert 'checked' in toggle_map['Product'], "Product column toggle should be checked by default"
