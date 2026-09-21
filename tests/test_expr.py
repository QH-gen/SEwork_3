"""expr：表达式树的求值、约束检查、序列化与规范化判重的测试。"""

import unittest
from fractions import Fraction

from arithmetic.expr import (
    Num,
    Op,
    canonical_key,
    check_constraints,
    evaluate,
    to_string,
)


class ToStringTest(unittest.TestCase):
    def test_simple_with_spaces(self):
        self.assertEqual(to_string(Op("+", Num(3), Num(5))), "3 + 5")

    def test_precedence(self):
        tree = Op("×", Op("+", Num(1), Num(2)), Num(3))
        self.assertEqual(to_string(tree), "(1 + 2) × 3")
        tree = Op("+", Num(1), Op("×", Num(2), Num(3)))
        self.assertEqual(to_string(tree), "1 + 2 × 3")

    def test_right_operand_keeps_parens(self):
        # 右操作数同级加括号，保证结合顺序被完整保留
        tree = Op("+", Num(1), Op("+", Num(2), Num(3)))
        self.assertEqual(to_string(tree), "1 + (2 + 3)")
        tree = Op("-", Num(5), Op("-", Num(2), Num(1)))
        self.assertEqual(to_string(tree), "5 - (2 - 1)")


class EvaluateTest(unittest.TestCase):
    def test_evaluate_fraction_ops(self):
        self.assertEqual(evaluate(Op("÷", Num(1), Num(2))), Fraction(1, 2))
        tree = Op("-", Num(Fraction(1, 2)), Num(Fraction(1, 3)))
        self.assertEqual(evaluate(tree), Fraction(1, 6))

    def test_evaluate_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            evaluate(Op("÷", Num(1), Num(0)))


class CanonicalKeyTest(unittest.TestCase):
    def test_commutative_duplicates(self):
        # 3 + (2 + 1) 与 (1 + 2) + 3 是重复题目
        a = Op("+", Num(3), Op("+", Num(2), Num(1)))
        b = Op("+", Op("+", Num(1), Num(2)), Num(3))
        self.assertEqual(canonical_key(a), canonical_key(b))
        # 6 × 8 与 8 × 6 是重复题目
        self.assertEqual(canonical_key(Op("×", Num(6), Num(8))),
                         canonical_key(Op("×", Num(8), Num(6))))

    def test_associativity_makes_difference(self):
        # 1 + 2 + 3 与 3 + 2 + 1 不是重复题目
        a = Op("+", Op("+", Num(1), Num(2)), Num(3))
        b = Op("+", Op("+", Num(3), Num(2)), Num(1))
        self.assertNotEqual(canonical_key(a), canonical_key(b))

    def test_non_commutative_not_merged(self):
        self.assertNotEqual(canonical_key(Op("-", Num(3), Num(5))),
                            canonical_key(Op("-", Num(5), Num(3))))


class ConstraintTest(unittest.TestCase):
    def test_subtraction_constraint(self):
        self.assertTrue(check_constraints(Op("-", Num(5), Num(3))))
        self.assertFalse(check_constraints(Op("-", Num(3), Num(5))))

    def test_division_constraint(self):
        self.assertTrue(check_constraints(Op("÷", Num(3), Num(5))))
        self.assertFalse(check_constraints(Op("÷", Num(5), Num(3))))  # 商大于 1
        self.assertFalse(check_constraints(Op("÷", Num(4), Num(2))))  # 商为整数
        self.assertFalse(check_constraints(Op("÷", Num(0), Num(3))))  # 商为 0
        self.assertFalse(check_constraints(Op("÷", Num(3), Num(0))))  # 除数为 0


if __name__ == "__main__":
    unittest.main()
