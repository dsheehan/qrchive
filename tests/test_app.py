import unittest
import sys
import os

# Add src to the search path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import app

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Matter Devices', response.data)
        self.assertIn(b'<table', response.data)

    def test_qrcode_route(self):
        response = self.app.get('/qrcode')
        self.assertEqual(response.status_code, 200)

    def test_matter_route(self):
        response = self.app.get('/matter')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]['Product'], 'Tapo S505D')

if __name__ == '__main__':
    unittest.main()
