"""parser：题目字符串解析的测试。"""

import unittest
from fractions import Fraction

from arithmetic.expr import Num, Op, canonical_key, evaluate
from arithmetic.parser import parse_expression, tokenize


class ParseTest(unittest.TestCase):
    def test_parse_precedence(self):
        self.assertEqual(evaluate(parse_expression("(1 + 2) × 3 ÷ 2")),
                         Fraction(9, 2))

    def test_parse_trailing_equals(self):
        self.assertEqual(evaluate(parse_expression("1/6 + 1/8 =")),
                         Fraction(7, 24))

    def test_parse_mixed_number(self):
        self.assertEqual(evaluate(parse_expression("2'3/8 + 1/8")),
                         Fraction(5, 2))

    def test_parse_ascii_operator_aliases(self):
        self.assertEqual(evaluate(parse_expression("3 * (4 - 1) / 2")),
                         Fraction(9, 2))

    def test_left_associativity(self):
        tree = parse_expression("1 + 2 + 3")
        expected = Op("+", Op("+", Num(1), Num(2)), Num(3))
        self.assertEqual(canonical_key(tree), canonical_key(expected))

    def test_roundtrip_with_to_string(self):
        for text in ["3 + 5", "1 + (2 + 3)", "(1 + 2) × 3",
                     "5 - (2 - 1)", "1 ÷ 2 + 1/6"]:
            self.assertEqual(
                canonical_key(parse_expression(to_string(parse_expression(text)))),
                canonical_key(parse_expression(text)),
            )

    def test_tokenize(self):
        self.assertEqual(
            tokenize("1 + 2 ="),
            [("num", "1"), ("op", "+"), ("num", "2"), ("eq", "=")],
        )

    def test_invalid_expressions(self):
        for bad in ["1 +", "(1 + 2", "1 $ 2", "", "1 + 2)"]:
            with self.assertRaises(ValueError):
                parse_expression(bad)


if __name__ == "__main__":
    unittest.main()
