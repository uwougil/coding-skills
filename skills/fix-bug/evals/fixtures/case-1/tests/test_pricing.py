import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.pricing import final_price


class PricingTests(unittest.TestCase):
    def test_zero_discount_preserves_price(self):
        self.assertEqual(final_price(100, 0), 100)


if __name__ == "__main__":
    unittest.main()
