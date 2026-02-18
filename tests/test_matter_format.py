import unittest
import sys
import os
import re

# Add src to the search path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

class TestMatterFormat(unittest.TestCase):
    def test_qr_code_layout_requirement(self):
        with open('src/static/js/matter.js', 'r') as f:
            content = f.read()
        
        # Check for the correct bit shifts based on the new layout
        self.assertIn('<< 3n', content)   # Discriminator
        self.assertIn('<< 15n', content)  # Passcode
        self.assertIn('<< 42n', content)  # Flow
        self.assertIn('<< 44n', content)  # Capabilities
        self.assertIn('<< 52n', content)  # Vendor ID
        self.assertIn('<< 68n', content)  # Product ID

    def test_manual_code_parsing(self):
        # Check if the JS has the logic to handle dashes
        with open('src/static/js/matter.js', 'r') as f:
            content = f.read()
        self.assertIn('.replace(/-/g, "")', content)

if __name__ == '__main__':
    unittest.main()
