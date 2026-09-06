import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.session import is_expired


class SessionTests(unittest.TestCase):
    def test_below_ttl_is_active(self):
        self.assertFalse(is_expired(9, 10))

    def test_above_ttl_is_expired(self):
        self.assertTrue(is_expired(11, 10))


if __name__ == "__main__":
    unittest.main()
