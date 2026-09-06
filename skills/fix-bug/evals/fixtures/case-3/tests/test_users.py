import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.users import display_name


class UserTests(unittest.TestCase):
    def test_display_name(self):
        self.assertEqual(display_name("  Alice  "), "alice")


if __name__ == "__main__":
    unittest.main()
