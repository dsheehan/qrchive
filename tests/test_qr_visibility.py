import unittest
import sys
import os

# Add src to the search path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import app

class TestQRColumnVisibility(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_qr_column_toggle_is_unchecked_by_default(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Find the column toggle for QR
        # It should NOT have the 'checked' attribute
        # We look for the label 'QR' and then its corresponding input
        # In the template:
        # <input class="form-check-input column-toggle" type="checkbox" value="{{ loop.index0 }}" id="col-toggle-{{ loop.index0 }}" {% if header != 'QR' %}checked{% endif %}>
        # <label class="form-check-label" for="col-toggle-{{ loop.index0 }}">{{ header }}</label>
        
        # Let's check for the specific line pattern for QR toggle
        # We need to know the index of QR in headers. 
        # From matter.csv: Product,Type,MAC,Pairing Code,Description,QR
        # QR is at index 5.
        
        qr_toggle_unchecked = b'id="col-toggle-5"'
        self.assertIn(qr_toggle_unchecked, response.data)
        
        # Ensure it doesn't have 'checked' right after the id (or anywhere in that input tag)
        # Actually, let's look for the whole tag to be sure.
        # It's harder to match exactly because of potentially varying order of attributes or whitespace.
        # But we can check that if it's "col-toggle-5", it doesn't have "checked" in the same tag.
        
        content = response.data.decode('utf-8')
        import re
        # Find the input tag for col-toggle-5
        match = re.search(r'<input[^>]+id="col-toggle-5"[^>]*>', content)
        self.assertIsNotNone(match, "Could not find QR column toggle input")
        tag = match.group(0)
        self.assertNotIn('checked', tag, "QR column toggle should not be checked by default")
        
        # Also verify other columns ARE checked
        match_product = re.search(r'<input[^>]+id="col-toggle-0"[^>]*>', content)
        self.assertIsNotNone(match_product)
        self.assertIn('checked', match_product.group(0), "Product column toggle should be checked by default")

if __name__ == '__main__':
    unittest.main()
