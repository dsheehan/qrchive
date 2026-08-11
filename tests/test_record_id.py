import re
import csv
import pytest
from record_id import (
    generate_id,
    is_safe_id,
    normalize_ids,
    DEFAULT_RECORD_ID_LENGTH,
    _BASE62_CHARS,
)


# --- ID generation ---

def test_generated_id_default_length():
    id_ = generate_id()
    assert len(id_) == DEFAULT_RECORD_ID_LENGTH == 5


def test_generated_id_is_base62():
    for _ in range(50):
        id_ = generate_id()
        assert re.match(r'^[A-Za-z0-9]+$', id_), f"Non-base62 id: {id_}"


def test_generated_id_custom_length():
    id_ = generate_id(length=8)
    assert len(id_) == 8


def test_generated_id_avoids_collision():
    existing = {'aaaaa', 'bbbbb'}
    for _ in range(20):
        id_ = generate_id(existing_ids=existing, length=5)
        assert id_ not in existing


# --- is_safe_id ---

def test_safe_ids_preserved():
    safe = ['device-1', 'device_1', 'device.1', 'device~1', 'abc', '123',
            '550e8400-e29b-41d4-a716-446655440000']
    for val in safe:
        assert is_safe_id(val), f"Expected safe: {val}"


def test_unsafe_ids_rejected():
    unsafe = ['device/1', 'device?1', 'device#1', 'device 1', 'device%201',
              'a&b', 'x=y', '', '   ']
    for val in unsafe:
        assert not is_safe_id(val), f"Expected unsafe: {val}"


# --- normalize_ids ---

def test_missing_id_column_gets_added():
    records = [{'Product': 'A'}, {'Product': 'B'}]
    result, changed = normalize_ids(records)
    assert changed
    for row in result:
        assert 'id' in row
        assert len(row['id']) == 5
        assert re.match(r'^[A-Za-z0-9]+$', row['id'])


def test_blank_ids_are_regenerated():
    records = [{'id': '', 'Product': 'A'}, {'id': '   ', 'Product': 'B'}]
    result, changed = normalize_ids(records)
    assert changed
    for row in result:
        assert row['id'].strip() != ''
        assert len(row['id']) == 5


def test_duplicate_ids_regenerate_after_first():
    records = [
        {'id': 'abc12', 'Product': 'Device A'},
        {'id': 'abc12', 'Product': 'Device B'},
    ]
    result, changed = normalize_ids(records)
    assert changed
    assert result[0]['id'] == 'abc12'
    assert result[1]['id'] != 'abc12'
    assert len(result[1]['id']) == 5


def test_unsafe_ids_are_regenerated():
    unsafe_ids = ['dev/1', 'dev?1', 'dev#1', 'dev 1', 'dev%1', 'a&b', 'x=y']
    for bad_id in unsafe_ids:
        records = [{'id': bad_id, 'Product': 'X'}]
        result, changed = normalize_ids(records)
        assert changed, f"Expected regeneration for: {bad_id}"
        assert result[0]['id'] != bad_id
        assert is_safe_id(result[0]['id'])


def test_safe_manual_ids_are_preserved():
    safe_ids = ['device-1', 'device_1', 'device.1', 'device~1',
                '550e8400-e29b-41d4-a716-446655440000']
    records = [{'id': id_, 'Product': 'X'} for id_ in safe_ids]
    result, changed = normalize_ids(records)
    assert not changed
    for row, expected_id in zip(result, safe_ids):
        assert row['id'] == expected_id


def test_all_unique_safe_ids_unchanged():
    records = [
        {'id': 'aaa11', 'Product': 'A'},
        {'id': 'bbb22', 'Product': 'B'},
    ]
    result, changed = normalize_ids(records)
    assert not changed
    assert result[0]['id'] == 'aaa11'
    assert result[1]['id'] == 'bbb22'


# --- API / repository integration ---

test_data_with_ids = [
    'id,Product,Type,MAC,Pairing Code,Description,QR',
    'abc12,Device A,Type1,11:22:33:44:55:66,123-456,Desc A,',
    'def34,Device B,Type2,AA:BB:CC:DD:EE:FF,789-012,Desc B,',
]

test_data_no_ids = [
    'Product,Type,MAC,Pairing Code,Description,QR',
    'Device A,Type1,11:22:33:44:55:66,123-456,Desc A,',
]


def test_csv_without_id_column_gets_ids(client, matter_data_path):
    temp_path = matter_data_path(test_data_no_ids)
    response = client.get('/matter')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert 'id' in data[0]
    assert len(data[0]['id']) == 5
    # Verify persisted
    with open(temp_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert 'id' in rows[0]
        assert len(rows[0]['id']) == 5


def test_update_by_id_allows_mac_change(client, matter_data_path):
    matter_data_path(test_data_with_ids)
    updated = {
        'Product': 'Device A Updated',
        'Type': 'Type1',
        'MAC': 'FF:FF:FF:FF:FF:FF',
        'Pairing Code': '123-456',
        'Description': 'Desc A',
        'QR': '',
    }
    response = client.put('/matter/abc12', json=updated)
    assert response.status_code == 200
    result = response.get_json()
    assert result['MAC'] == 'FF:FF:FF:FF:FF:FF'
    assert result['id'] == 'abc12'


def test_delete_by_id_removes_correct_record(client, matter_data_path):
    temp_path = matter_data_path(test_data_with_ids)
    response = client.delete('/matter/abc12')
    assert response.status_code == 200
    with open(temp_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 1
    assert rows[0]['id'] == 'def34'


def test_csv_persisted_after_id_normalization(client, matter_data_path):
    temp_path = matter_data_path(test_data_no_ids)
    # Trigger normalization via GET
    client.get('/matter')
    with open(temp_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert 'id' in content.split('\n')[0]
