import unittest
import interval

class IntervalParserTestCase(unittest.TestCase):
    '''Test the parse_interval function'''
    def test_parse_well_formed_intervals(self):
        self.assertEqual(interval.parse_interval("[0, 1]"), (True, 0,1,True))
        self.assertEqual(interval.parse_interval("[ 10, 1)"), (True, 10,1,False))
        self.assertEqual(interval.parse_interval("[-70,+1]"), (True, -70,1,True))

    def test_parse_malformed_intervals_raise_exceptions(self):
        with self.assertRaises(interval.IntervalParseException):
            interval.parse_interval("-1 1")
        with self.assertRaises(interval.IntervalParseException):
            interval.parse_interval("[-1 1,1]")
        with self.assertRaises(interval.IntervalParseException):
            interval.parse_interval("[-11,]")
        with self.assertRaises(interval.IntervalParseException):
            interval.parse_interval("{1,1]")
        with self.assertRaises(interval.IntervalParseException):
            interval.parse_interval("(-1.0,1]")

class IntervalClassTestCase(unittest.TestCase):
    '''Test the interval class'''
    def test_valid_interval_creation_and_representation(self):
        intvl1 = interval.interval("[0, 1]")
        self.assertEqual(str(intvl1), "[0, 1]")
        intvl2 = interval.interval("( -10 , +1)")
        self.assertEqual(intvl2.__str__(), "(-10, 1)")
        intvl3 = interval.interval("  [ -3, 3 )")
        self.assertEqual(intvl3.__str__(), "[-3, 3)")
        intvl4 = interval.interval("[1, 1]")
        self.assertEqual(intvl4.__str__(), "[1, 1]")
        intvl5 = interval.interval("[1, 2)")
        self.assertEqual(intvl5.__str__(), "[1, 2)")

    def test_invalid_intervals_do_not_validate(self):
        with self.assertRaises(interval.InvalidIntervalException):
            intvl1 = interval.interval("(1, 1)")
        with self.assertRaises(interval.InvalidIntervalException):
            intvl2 = interval.interval("(-1, -3)")
        with self.assertRaises(interval.InvalidIntervalException):
            intvl3 = interval.interval("[3, 1]")
        with self.assertRaises(interval.InvalidIntervalException):
            intvl4 = interval.interval("(1, 1]")

    def test_interval_contains(self):
        intvl1 = interval.interval("[1, 3]")
        for n in (1, 2, 3):
            self.assertTrue(intvl1.contains(n))
        self.assertFalse(intvl1.contains(0))
        self.assertFalse(intvl1.contains(4))

        intvl2 = interval.interval("(1, 3)")
        self.assertTrue(intvl2.contains(2))
        self.assertFalse(intvl2.contains(1))
        self.assertFalse(intvl2.contains(3))

        intvl3 = interval.interval("(-3, 1]")
        for n in (-2, -1, 0, 1):
            self.assertTrue(intvl3.contains(n))
        self.assertFalse(intvl3.contains(-3))
        self.assertFalse(intvl3.contains(2))

        # In a future version, we may allow non-integer tests, but not now
        self.assertFalse(intvl3.contains(-3.0)) # Allow anything that can be cast to integer
        with self.assertRaises(ValueError):
            self.assertTrue(intvl3.contains(-2.5))
        with self.assertRaises(ValueError):
            self.assertTrue(intvl3.contains(0.999))
        with self.assertRaises(ValueError):
            self.assertFalse(intvl3.contains(1.01))

class MergeIntervalsTestCase(unittest.TestCase):
    '''Test the mergeIntervals function'''

    def test_merge_overlapping_intervals(self):
        # Overlapping
        self.assertEqual(
            interval.mergeIntervals(interval.interval("[0, 3]"),
                                    interval.interval("[1, 5]")),
            interval.interval("[0, 5]")
            )
        self.assertEqual(
            interval.mergeIntervals(interval.interval("[0, 3]"),
                                    interval.interval("[3, 5]")),
            interval.interval("[0, 5]")
            )
        # One contains the other
        self.assertEqual(
            interval.mergeIntervals(interval.interval("[0, 5]"),
                                    interval.interval("[1, 3]")),
            interval.interval("[0, 5]")
            )
        # Open/closed
        self.assertEqual(
            interval.mergeIntervals(interval.interval("(0, 5)"),
                                    interval.interval("[1, 5]")),
            interval.interval("(0, 5]")
            )
        # Negative
        self.assertEqual(
            interval.mergeIntervals(interval.interval("(-3, 3)"),
                                    interval.interval("[-3, 0)")),
            interval.interval("[-3, 3)")
            )

    def test_merge_adjacent_intervals(self):
        self.assertEqual(
            interval.mergeIntervals(interval.interval("[0, 3]"),
                                    interval.interval("[4, 5]")),
            interval.interval("[0, 5]")
            )
        self.assertEqual(
            interval.mergeIntervals(interval.interval("[0, 3)"),
                                    interval.interval("[3, 5]")),
            interval.interval("[0, 5]")
            )
        self.assertEqual(
            interval.mergeIntervals(interval.interval("[-3, 0)"),
                                    interval.interval("[0, 3]")),
            interval.interval("[-3, 3]")
            )

    def test_merge_unmergable_intervalse_raises_exception(self):
        with self.assertRaises(IntervalMergeException):
            interval.mergeIntervals(interval.interval("[-3, 0)"),
                                    interval.interval("(0, 3]"))

        with self.assertRaises(IntervalMergeException):
            interval.mergeIntervals(interval.interval("[-3, 1)"),
                                    interval.interval("[2, 3]"))

        with self.assertRaises(IntervalMergeException):
            interval.mergeIntervals(interval.interval("[-3, 0)"),
                                    interval.interval("[3, 4]"))
