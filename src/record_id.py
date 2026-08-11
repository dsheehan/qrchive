import os
import re
import secrets

DEFAULT_RECORD_ID_LENGTH = 5
_BASE62_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
_SAFE_ID_PATTERN = re.compile(r'^[A-Za-z0-9._~-]+$')


def get_record_id_length():
    raw = os.getenv('QRCHIVE_RECORD_ID_LENGTH', '')
    try:
        length = int(raw)
        if length <= 0:
            return DEFAULT_RECORD_ID_LENGTH
        return length
    except (ValueError, TypeError):
        return DEFAULT_RECORD_ID_LENGTH


def is_safe_id(value):
    if not value or not value.strip():
        return False
    return bool(_SAFE_ID_PATTERN.match(value.strip()))


def generate_id(existing_ids=None, length=None):
    if length is None:
        length = get_record_id_length()
    if existing_ids is None:
        existing_ids = set()
    while True:
        new_id = ''.join(secrets.choice(_BASE62_CHARS) for _ in range(length))
        if new_id not in existing_ids:
            return new_id


def normalize_ids(records):
    """
    Ensure every record has a safe, unique 'id' field.
    Returns (normalized_records, changed) where changed=True if any IDs were added/modified.
    """
    changed = False
    seen_ids = set()
    result = []

    for record in records:
        record_id = record.get('id', '').strip() if record.get('id') else ''

        if record_id and is_safe_id(record_id) and record_id not in seen_ids:
            seen_ids.add(record_id)
        else:
            new_id = generate_id(existing_ids=seen_ids)
            record = dict(record)
            record['id'] = new_id
            seen_ids.add(new_id)
            changed = True

        result.append(record)

    return result, changed
