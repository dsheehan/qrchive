from services import read_csv_file, write_csv_file
from record_id import normalize_ids, generate_id, is_safe_id


class MatterRepository:
    def __init__(self, data_path):
        self.data_path = data_path

    def _read_csv(self):
        data, headers = read_csv_file(self.data_path)
        if data is None:
            data = []
        if headers is None:
            headers = []

        # Ensure 'id' is the first column
        if headers and 'id' not in headers:
            headers = ['id'] + list(headers)

        normalized, changed = normalize_ids(data)

        if changed:
            # Persist the normalized data so IDs are stable
            self._write_csv(normalized, headers)

        return normalized, headers

    def _write_csv(self, data, headers):
        write_csv_file(self.data_path, data, headers)

    def get_all(self):
        return self._read_csv()

    def get_by_id(self, record_id):
        data, _ = self._read_csv()
        for row in data:
            if row.get('id') == record_id:
                return row
        return None

    def add(self, device):
        data, headers = self._read_csv()

        # Assign a new id (ignore any client-supplied id)
        existing_ids = {row.get('id') for row in data if row.get('id')}
        device = dict(device)
        device['id'] = generate_id(existing_ids=existing_ids)

        # Ensure headers include all keys from the new device
        for key in device:
            if key not in headers:
                headers.append(key)

        data.append(device)
        self._write_csv(data, headers)
        return device

    def update(self, record_id, updated_device):
        data, headers = self._read_csv()
        found = False
        for i, row in enumerate(data):
            if row.get('id') == record_id:
                updated = dict(updated_device)
                updated['id'] = record_id  # preserve the id
                data[i] = updated
                found = True
                break

        if not found:
            return None

        self._write_csv(data, headers)
        return updated

    def delete(self, record_id):
        data, headers = self._read_csv()
        new_data = [row for row in data if row.get('id') != record_id]

        if len(new_data) == len(data):
            return False

        self._write_csv(new_data, headers)
        return True

    def bulk_add(self, new_records):
        data, headers = self._read_csv()
        existing_ids = {row.get('id') for row in data if row.get('id')}

        # Normalize IDs in the imported records, avoiding collisions with existing
        added_count = 0
        for record in new_records:
            record = dict(record)
            record_id = record.get('id', '').strip() if record.get('id') else ''
            if record_id and is_safe_id(record_id) and record_id not in existing_ids:
                pass  # keep the id
            else:
                record['id'] = generate_id(existing_ids=existing_ids)

            existing_ids.add(record['id'])

            # Ensure headers include all keys
            for key in record:
                if key not in headers:
                    headers.append(key)

            data.append(record)
            added_count += 1

        self._write_csv(data, headers)
        return added_count
