"""numfmt：数值格式化与解析的测试（需求 7/8 的分数格式）。"""

import unittest
from fractions import Fraction

from arithmetic.numfmt import format_number, parse_number


class FormatNumberTest(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(format_number(Fraction(0)), "0")
        self.assertEqual(format_number(Fraction(42)), "42")

    def test_proper_fraction(self):
        self.assertEqual(format_number(Fraction(3, 5)), "3/5")
        self.assertEqual(format_number(Fraction(7, 24)), "7/24")

    def test_mixed_fraction(self):
        self.assertEqual(format_number(Fraction(19, 8)), "2'3/8")
        self.assertEqual(format_number(Fraction(5, 2)), "2'1/2")


class ParseNumberTest(unittest.TestCase):
    def test_parse_basic_forms(self):
        self.assertEqual(parse_number("5"), Fraction(5))
        self.assertEqual(parse_number("3/5"), Fraction(3, 5))
        self.assertEqual(parse_number("2'3/8"), Fraction(19, 8))

    def test_parse_unicode_apostrophe(self):
        self.assertEqual(parse_number("2’3/8"), Fraction(19, 8))

    def test_roundtrip(self):
        for text in ["0", "9", "1/2", "7/24", "2'3/8", "10'11/12"]:
            self.assertEqual(format_number(parse_number(text)), text)

    def test_invalid_number(self):
        for bad in ["2'8/8", "3/0", "abc", ""]:
            with self.assertRaises(ValueError):
                parse_number(bad)


if __name__ == "__main__":
    unittest.main()
