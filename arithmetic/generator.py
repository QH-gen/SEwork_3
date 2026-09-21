"""随机生成满足全部约束且互不重复的四则运算题目。

生成策略：自底向上构造表达式树，构造过程中同步计算子表达式的精确值
（Fraction），在减法节点上通过交换左右子树保证 e1 >= e2，在除法节点上
保证商为真分数（不可行时就地换成其他运算符）。这样构造出的树天然满足
需求 3/4，无需生成后再整棵校验，也不存在丢弃重来的开销。

判重（需求 6）：用 expr.canonical_key 作为键放入集合。
"""

import random
from fractions import Fraction

from .expr import Num, Op, canonical_key

_OPS = ["+", "-", "×", "÷"]
_WEIGHTS = [3, 3, 3, 2]  # 除法约束较严，适当降低其出现权重
_MAX_CONSECUTIVE_DUPLICATES = 10000


class QuestionSpaceExhausted(RuntimeError):
    """给定范围内互不重复的题目数量不足，无法满足 -n。"""


def _random_operand(value_range, rng):
    """生成叶子操作数：自然数（0 ~ r-1）或真分数（分母小于 r）。"""
    if value_range >= 3 and rng.random() < 0.3:
        denominator = rng.randint(2, value_range - 1)
        numerator = rng.randint(1, denominator - 1)
        return Fraction(numerator, denominator)
    return Fraction(rng.randint(0, value_range - 1))


def _generate_node(op_slots, value_range, rng):
    """构造含 op_slots 个运算符的子表达式，返回 (节点, 精确值)。

    返回的子表达式保证：减法结果非负、除法商为真分数、除数非 0。
    """
    if op_slots == 0:
        value = _random_operand(value_range, rng)
        return Num(value), value

    left_slots = rng.randint(0, op_slots - 1)
    right_slots = op_slots - 1 - left_slots
    left, left_value = _generate_node(left_slots, value_range, rng)
    right, right_value = _generate_node(right_slots, value_range, rng)
    op = rng.choices(_OPS, weights=_WEIGHTS, k=1)[0]

    if op == "÷":
        # 除法：商必须是真分数，即 0 < 被除数 < 除数；两个方向都试一下
        if right_value != 0 and 0 < left_value / right_value < 1:
            return Op("÷", left, right), left_value / right_value
        if left_value != 0 and 0 < right_value / left_value < 1:
            return Op("÷", right, left), right_value / left_value
        # 两个方向都不可行（如 r=1 时操作数全为 0），就地换成其他运算符，
        # 避免丢弃已构造好的子树造成重复计算
        op = rng.choice(["+", "-", "×"])

    if op == "+":
        return Op("+", left, right), left_value + right_value
    if op == "×":
        return Op("×", left, right), left_value * right_value
    # 减法：保证 e1 >= e2，不够减就交换左右子树
    if left_value < right_value:
        left, right = right, left
    return Op("-", left, right), abs(left_value - right_value)


def generate_questions(count, value_range, rng=None):
    """生成 count 道互不重复、满足全部约束的题目。

    :param count: 题目数量（-n）
    :param value_range: 数值范围上界（-r），数值取 0 ~ r-1
    :param rng: 可选的 random.Random 实例（便于测试复现）
    :raises QuestionSpaceExhausted: 范围内题目空间不足
    """
    if value_range < 1:
        raise ValueError("数值范围 -r 必须是正整数")
    if count < 1:
        raise ValueError("题目数量 -n 必须是正整数")
    if rng is None:
        rng = random.Random()

    questions = []
    seen = set()
    consecutive_duplicates = 0
    while len(questions) < count:
        op_slots = rng.randint(1, 3)  # 需求 5：运算符个数 1 ~ 3
        tree, _ = _generate_node(op_slots, value_range, rng)
        key = canonical_key(tree)
        if key in seen:
            consecutive_duplicates += 1
            if consecutive_duplicates > _MAX_CONSECUTIVE_DUPLICATES:
                raise QuestionSpaceExhausted(
                    f"在 0~{value_range - 1} 的数值范围内只能构造出 "
                    f"{len(questions)} 道互不重复的题目，无法满足 -n {count}，"
                    f"请增大 -r 或减小 -n"
                )
            continue
        consecutive_duplicates = 0
        seen.add(key)
        questions.append(tree)
    return questions
