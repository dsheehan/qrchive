import unittest
import sys
import os
import json
import csv
import tempfile

# Add src to the search path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import app, get_data_path

class TestDeleteWorkflow(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Create a temporary CSV file
        self.fd, self.temp_path = tempfile.mkstemp(suffix='.csv')
        os.close(self.fd)
        
        # Set up some initial data
        self.headers = ['Product', 'Type', 'MAC', 'Pairing Code', 'Description', 'QR']
        self.initial_data = [
            {'Product': 'Device1', 'Type': 'Type1', 'MAC': '11:22:33:44:55:66', 'Pairing Code': '123-456', 'Description': 'Desc1', 'QR': 'QR1'},
            {'Product': 'Device2', 'Type': 'Type2', 'MAC': 'AA:BB:CC:DD:EE:FF', 'Pairing Code': '789-012', 'Description': 'Desc2', 'QR': 'QR2'}
        ]
        
        with open(self.temp_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(self.initial_data)
        
        # Override the data path
        os.environ['MATTER_DATA_PATH'] = self.temp_path

    def tearDown(self):
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)
        if 'MATTER_DATA_PATH' in os.environ:
            del os.environ['MATTER_DATA_PATH']

    def test_delete_device_success(self):
        # Delete Device1
        mac_to_delete = '11:22:33:44:55:66'
        response = self.app.delete(f'/matter/{mac_to_delete}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})
        
        # Verify it's gone from the CSV
        with open(self.temp_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['MAC'], 'AA:BB:CC:DD:EE:FF')

    def test_delete_device_not_found(self):
        # Try to delete non-existent device
        mac_to_delete = '00:00:00:00:00:00'
        response = self.app.delete(f'/matter/{mac_to_delete}')
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.get_json())
        
        # Verify CSV is unchanged
        with open(self.temp_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            self.assertEqual(len(data), 2)

if __name__ == '__main__':
    unittest.main()
