import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.titles import normalize_title


class TitleTests(unittest.TestCase):
    def test_two_spaces(self):
        self.assertEqual(normalize_title("Alpha  Beta"), "Alpha Beta")


if __name__ == "__main__":
    unittest.main()
