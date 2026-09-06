import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.ranges import inclusive_range


class RangeTests(unittest.TestCase):
    def test_closed_interval(self):
        self.assertEqual(inclusive_range(2, 4), [2, 3, 4])


if __name__ == "__main__":
    unittest.main()
