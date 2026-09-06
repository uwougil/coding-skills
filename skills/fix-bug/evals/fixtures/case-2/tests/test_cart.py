import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.cart import line_total


class CartTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(line_total(7, 1), 7)


if __name__ == "__main__":
    unittest.main()
