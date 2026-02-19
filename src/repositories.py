import csv
import os

class MatterRepository:
    def __init__(self, data_path):
        self.data_path = data_path

    def _read_csv(self):
        data = []
        headers = []
        try:
            with open(self.data_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            pass
        return data, headers

    def _write_csv(self, data, headers):
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

    def get_all(self):
        data, headers = self._read_csv()
        return data, headers

    def get_by_mac(self, mac):
        data, _ = self._read_csv()
        for row in data:
            if row.get('MAC') == mac:
                return row
        return None

    def add(self, device):
        data, headers = self._read_csv()
        
        # Validation: MAC should be unique if provided
        mac = device.get('MAC')
        if mac:
            for row in data:
                if row.get('MAC') == mac:
                    raise ValueError(f"Device with MAC {mac} already exists")
        
        data.append(device)
        self._write_csv(data, headers)
        return device

    def update(self, mac, updated_device):
        data, headers = self._read_csv()
        found = False
        for i, row in enumerate(data):
            if row.get('MAC') == mac:
                data[i] = updated_device
                found = True
                break
        
        if not found:
            return None
            
        self._write_csv(data, headers)
        return updated_device

    def delete(self, mac):
        data, headers = self._read_csv()
        found = False
        new_data = []
        for row in data:
            if row.get('MAC') == mac:
                found = True
                continue
            new_data.append(row)
        
        if not found:
            return False
            
        self._write_csv(new_data, headers)
        return True
