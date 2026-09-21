"""把四则运算题目字符串解析为表达式树。

支持 ``+ - × ÷``（也兼容 ``* /`` 和 Unicode 减号 ``−``）、括号、
自然数 / 真分数 / 带分数，以及题目末尾的 ``=``。

文法（递归下降，左结合）::

    expr   := term (('+' | '-') term)*
    term   := factor (('×' | '÷') factor)*
    factor := NUMBER | '(' expr ')'
"""

import re

from .expr import Num, Op
from .numfmt import parse_number

_TOKEN_RE = re.compile(
    r"\s*(?:(\d+'\d+/\d+|\d+/\d+|\d+)|([+\-−×÷*/()=]))"
)
_OP_ALIASES = {
    "+": "+", "-": "-", "−": "-", "×": "×", "*": "×", "÷": "÷", "/": "÷",
}


def tokenize(text):
    tokens = []
    pos = 0
    while pos < len(text):
        match = _TOKEN_RE.match(text, pos)
        if match is None:
            if text[pos:].strip() == "":
                break
            raise ValueError(f"无法解析的字符: {text[pos]!r}")
        pos = match.end()
        number, symbol = match.groups()
        if number is not None:
            tokens.append(("num", number))
        elif symbol in _OP_ALIASES:
            tokens.append(("op", _OP_ALIASES[symbol]))
        elif symbol in "()":
            tokens.append(("paren", symbol))
        else:  # '='
            tokens.append(("eq", symbol))
    return tokens


class _Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _advance(self):
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def parse(self):
        node = self._expr()
        if self.peek() is not None:
            raise ValueError(f"表达式后有多余内容: {self.peek()[1]!r}")
        return node

    def _expr(self):
        node = self._term()
        while True:
            token = self.peek()
            if token is not None and token[0] == "op" and token[1] in ("+", "-"):
                self._advance()
                node = Op(token[1], node, self._term())
            else:
                return node

    def _term(self):
        node = self._factor()
        while True:
            token = self.peek()
            if token is not None and token[0] == "op" and token[1] in ("×", "÷"):
                self._advance()
                node = Op(token[1], node, self._factor())
            else:
                return node

    def _factor(self):
        token = self.peek()
        if token is None:
            raise ValueError("表达式不完整")
        if token[0] == "num":
            self._advance()
            return Num(parse_number(token[1]))
        if token == ("paren", "("):
            self._advance()
            node = self._expr()
            if self.peek() != ("paren", ")"):
                raise ValueError("缺少右括号")
            self._advance()
            return node
        raise ValueError(f"意外的记号: {token[1]!r}")


def parse_expression(text):
    """解析 ``3 + 5 =`` 或 ``(1 + 2) × 3`` 形式的表达式，返回表达式树。"""
    tokens = tokenize(text)
    if tokens and tokens[-1] == ("eq", "="):
        tokens = tokens[:-1]
    if not tokens:
        raise ValueError("空表达式")
    return _Parser(tokens).parse()
