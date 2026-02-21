import unittest
import sys
import os
import csv
import io

# Add src to the search path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import app, get_data_path

class ImportExportTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Backup original data path
        self.original_data_path = get_data_path()
        self.test_data_path = os.path.join(os.getcwd(), 'data', 'test_matter.csv')
        os.environ['MATTER_DATA_PATH'] = self.test_data_path
        
        # Create a test CSV
        with open(self.test_data_path, 'w', encoding='utf-8', newline='') as f:
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

    def tearDown(self):
        if os.path.exists(self.test_data_path):
            os.remove(self.test_data_path)
        # Restore environment variable
        if 'MATTER_DATA_PATH' in os.environ:
            del os.environ['MATTER_DATA_PATH']

    def test_export(self):
        response = self.app.get('/matter/export')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/csv')
        self.assertIn(b'AA:BB:CC:DD:EE:FF', response.data)

    def test_import(self):
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
        
        response = self.app.post('/matter/import', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        self.assertEqual(json_data['added_count'], 1) # Only one should be added due to de-duplication
        
        # Verify content
        response = self.app.get('/matter')
        data = response.get_json()
        macs = [item['MAC'] for item in data]
        self.assertIn('11:22:33:44:55:66', macs)
        self.assertIn('AA:BB:CC:DD:EE:FF', macs)
        self.assertEqual(len(data), 2)

if __name__ == '__main__':
    unittest.main()
