import unittest
import sys
import os

# Add src to the search path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_matter_table_is_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Matter Devices', response.data)
        self.assertIn(b'<table', response.data)
        self.assertIn(b'Tapo S505D', response.data) # Check if data from CSV is present

    def test_matter_table_has_qr_column(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<th>QR Code</th>', response.data)
        self.assertIn(b'Show QR', response.data)

if __name__ == '__main__':
    unittest.main()
