import unittest

from src.suppression_media import is_hard_bounce


class HardBounceTest(unittest.TestCase):
    def test_only_hard_bounce_events_are_suppressed(self):
        self.assertTrue(is_hard_bounce([{"type": "delivered"}, {"type": "hard_bounce"}]))
        self.assertFalse(is_hard_bounce([{"type": "delivered"}]))


if __name__ == "__main__":
    unittest.main()
