"""数值（自然数 / 真分数 / 带分数）的格式化与解析。

约定：
- 自然数直接输出，如 ``5``；
- 真分数（值小于 1）输出为 ``分子/分母``，如 ``3/5``；
- 假分数（值大于等于 1 且非整数）输出为带分数 ``整数'分子/分母``，如 ``2'3/8``。
"""

from fractions import Fraction

_APOSTROPHES = "'’′"


def format_number(value):
    """把 Fraction 格式化为题目/答案文件中的字符串形式。"""
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    if value < 1:
        return f"{value.numerator}/{value.denominator}"
    whole = value.numerator // value.denominator
    remainder = value - whole
    return f"{whole}'{remainder.numerator}/{remainder.denominator}"


def parse_number(text):
    """解析 ``5`` / ``3/5`` / ``2'3/8`` 形式的数字，返回 Fraction。"""
    text = text.strip()
    for apostrophe in _APOSTROPHES:
        text = text.replace(apostrophe, "'")
    if "'" in text:
        whole_text, frac_text = text.split("'", 1)
        num_text, den_text = frac_text.split("/", 1)
        whole, numerator, denominator = int(whole_text), int(num_text), int(den_text)
        if whole < 0 or numerator <= 0 or denominator <= 0 or numerator >= denominator:
            raise ValueError(f"非法带分数: {text!r}")
        return Fraction(whole) + Fraction(numerator, denominator)
    if "/" in text:
        num_text, den_text = text.split("/", 1)
        numerator, denominator = int(num_text), int(den_text)
        if numerator < 0 or denominator <= 0:
            raise ValueError(f"非法分数: {text!r}")
        return Fraction(numerator, denominator)
    return Fraction(int(text))
