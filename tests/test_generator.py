"""generator：题目生成的约束、判重与边界测试（需求 3~6、9）。"""

import random
import time
import unittest

from arithmetic.expr import (
    Num,
    check_constraints,
    evaluate,
    operator_count,
    canonical_key,
)
from arithmetic.generator import QuestionSpaceExhausted, generate_questions


def iter_leaves(node):
    if isinstance(node, Num):
        yield node.value
    else:
        yield from iter_leaves(node.left)
        yield from iter_leaves(node.right)


class GeneratorTest(unittest.TestCase):
    def test_basic_properties(self):
        questions = generate_questions(200, 10, rng=random.Random(1))
        self.assertEqual(len(questions), 200)
        keys = set()
        for question in questions:
            self.assertLessEqual(operator_count(question), 3)  # 需求 5
            self.assertGreaterEqual(operator_count(question), 1)
            self.assertTrue(check_constraints(question))  # 需求 3/4
            evaluate(question)  # 全程可求值，无异常
            keys.add(canonical_key(question))
        self.assertEqual(len(keys), 200)  # 需求 6：互不重复

    def test_operand_range(self):
        questions = generate_questions(300, 5, rng=random.Random(2))
        for question in questions:
            for value in iter_leaves(question):  # 需求 2：数值小于 r
                self.assertLess(value, 5)
                self.assertGreaterEqual(value, 0)

    def test_value_range_one(self):
        questions = generate_questions(5, 1)
        self.assertEqual(len(questions), 5)
        for question in questions:
            self.assertTrue(check_constraints(question))

    def test_space_exhausted(self):
        with self.assertRaises(QuestionSpaceExhausted):
            generate_questions(5000, 1)

    def test_ten_thousand_questions(self):  # 需求 9
        start = time.perf_counter()
        questions = generate_questions(10000, 50, rng=random.Random(42))
        elapsed = time.perf_counter() - start
        self.assertEqual(len(questions), 10000)
        self.assertLess(elapsed, 60)
        print(f"\n[性能] 生成 10000 道题目耗时 {elapsed:.2f} 秒")


if __name__ == "__main__":
    unittest.main()
