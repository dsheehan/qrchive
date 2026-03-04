from services import read_csv_file, write_csv_file

class MatterRepository:
    def __init__(self, data_path):
        self.data_path = data_path

    def _read_csv(self):
        return read_csv_file(self.data_path)

    def _write_csv(self, data, headers):
        write_csv_file(self.data_path, data, headers)

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

    def bulk_add(self, new_records):
        data, headers = self._read_csv()
        existing_macs = {row.get('MAC') for row in data if row.get('MAC')}
        
        added_count = 0
        for record in new_records:
            mac = record.get('MAC')
            if mac and mac not in existing_macs:
                data.append(record)
                existing_macs.add(mac)
                added_count += 1
            elif not mac:
                # If no MAC, we just append it? 
                # The issue says "de-duplicated", usually MAC is the unique ID here.
                # If there's no MAC, we can't easily de-duplicate, but maybe we should allow it.
                data.append(record)
                added_count += 1
        
        self._write_csv(data, headers)
        return added_count
