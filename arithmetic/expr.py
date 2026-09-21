"""算术表达式树的定义、求值、约束检查、序列化与规范化。

表达式文法::

    e = n | e1 + e2 | e1 - e2 | e1 × e2 | e1 ÷ e2 | (e)

其中 n 为自然数或真分数。表达式用 ``Num``（叶子）和 ``Op``（二元运算）表示。
"""

from fractions import Fraction

from .numfmt import format_number

PRECEDENCE = {"+": 1, "-": 1, "×": 2, "÷": 2}
_COMMUTATIVE = {"+", "×"}


class Num:
    """叶子节点：一个自然数或真分数。"""

    __slots__ = ("value",)

    def __init__(self, value):
        self.value = Fraction(value)


class Op:
    """内部节点：二元运算 op(left, right)。"""

    __slots__ = ("op", "left", "right")

    def __init__(self, op, left, right):
        if op not in PRECEDENCE:
            raise ValueError(f"未知运算符: {op!r}")
        self.op = op
        self.left = left
        self.right = right


def operator_count(node):
    """统计表达式中的运算符个数（需求 5：不超过 3 个）。"""
    if isinstance(node, Num):
        return 0
    return 1 + operator_count(node.left) + operator_count(node.right)


def evaluate(node):
    """精确求值（基于 Fraction），除数为 0 时抛出 ZeroDivisionError。"""
    if isinstance(node, Num):
        return node.value
    left = evaluate(node.left)
    right = evaluate(node.right)
    if node.op == "+":
        return left + right
    if node.op == "-":
        return left - right
    if node.op == "×":
        return left * right
    if right == 0:
        raise ZeroDivisionError("除数为 0")
    return left / right


def check_constraints(node):
    """检查题目约束（需求 3/4）：

    - 减法子表达式 e1 - e2 满足 e1 >= e2（过程不产生负数）；
    - 除法子表达式 e1 ÷ e2 的商是真分数（0 < 商 < 1）。
    """
    if isinstance(node, Num):
        return True
    if not check_constraints(node.left) or not check_constraints(node.right):
        return False
    left = evaluate(node.left)
    right = evaluate(node.right)
    if node.op == "-" and left < right:
        return False
    if node.op == "÷":
        if right == 0:
            return False
        quotient = left / right
        if not 0 < quotient < 1:
            return False
    return True


def to_string(node):
    """序列化为带空格分隔的最小括号形式，如 ``(1 + 2) × 3``。

    括号规则：右操作数与父节点优先级相同时也加括号（如 ``1 + (2 + 3)``），
    以保证字符串解析回去后与原表达式树完全一致（保持结合顺序）。
    """
    return _format(node, 0, False)


def _format(node, parent_prec, is_right_operand):
    if isinstance(node, Num):
        return format_number(node.value)
    prec = PRECEDENCE[node.op]
    text = (
        _format(node.left, prec, False)
        + f" {node.op} "
        + _format(node.right, prec, True)
    )
    if prec < parent_prec or (prec == parent_prec and is_right_operand):
        return f"({text})"
    return text


def canonical_key(node):
    """计算题目的规范化键，用于判重（需求 6）。

    两道题目能通过有限次交换 ``+`` / ``×`` 左右算术表达式互相变换，
    当且仅当它们的 canonical_key 相同。做法：递归规范化两个子树后，
    对可交换运算符把两个子键按大小排序。注意这里不做结合律展开，
    因此 ``1 + 2 + 3``（即 ``(1 + 2) + 3``）与 ``3 + 2 + 1``
    （即 ``(3 + 2) + 1``）的键不同，是两道不重复的题目。
    """
    if isinstance(node, Num):
        return ("num", node.value)
    left = canonical_key(node.left)
    right = canonical_key(node.right)
    if node.op in _COMMUTATIVE and right < left:
        left, right = right, left
    return (node.op, left, right)
