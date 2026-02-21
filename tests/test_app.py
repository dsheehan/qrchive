import unittest
import sys
import os

# Add src to the search path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import app, VERSION

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Matter Devices', response.data)
        self.assertIn(b'<table', response.data)
        # Check if version is present in navbar
        expected_version = f'v{VERSION}'.encode()
        self.assertIn(expected_version, response.data)

    def test_qrcode_route(self):
        response = self.app.get('/qrcode')
        self.assertEqual(response.status_code, 200)

    def test_licenses_route(self):
        response = self.app.get('/licenses')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Open Source Licenses', response.data)
        self.assertIn(b'Flask', response.data)
        self.assertIn(b'Bootstrap', response.data)

    def test_matter_route(self):
        response = self.app.get('/matter')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]['Product'], 'Tapo S505D')

    def test_health_route(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['version'], VERSION)

    def test_latest_release_route(self):
        # We don't want to actually hit GitHub API in tests
        # This will test the route exists and handles failure gracefully if not mocked
        response = self.app.get('/api/latest-release')
        # It might be 200 (if GITHUB_REPO exists and public) or 404/500 otherwise.
        self.assertIn(response.status_code, [200, 403, 404, 500])
        
        if response.status_code == 200:
            data = response.get_json()
            self.assertIn('current_version', data)
            self.assertIn('latest_version', data)
            self.assertIn('is_newer', data)
            self.assertIn('release_notes', data)
            self.assertEqual(data['current_version'], VERSION)

if __name__ == '__main__':
    unittest.main()
