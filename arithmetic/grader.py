"""对给定的题目文件与答案文件判分，统计对错并输出 Grade.txt。"""

import re

from .expr import evaluate
from .numfmt import parse_number
from .parser import parse_expression

_LINE_RE = re.compile(r"^\s*(\d+)\s*\.\s*(.+?)\s*$")


def _read_records(path):
    """读取 ``1. 内容`` 格式的文件，返回 [(编号, 内容), ...]。"""
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = _LINE_RE.match(line)
            if match is None:
                raise ValueError(f"无法解析的行: {line!r}")
            records.append((int(match.group(1)), match.group(2)))
    return records


def grade(exercise_path, answer_path, output_path="Grade.txt"):
    """判定答案对错并统计数量，结果写入 output_path。

    返回 (正确编号列表, 错误编号列表)。解析失败或答案缺失按错误计。
    """
    exercises = _read_records(exercise_path)
    answers = dict(_read_records(answer_path))

    correct, wrong = [], []
    for number, question_text in exercises:
        try:
            value = evaluate(parse_expression(question_text))
            expected = parse_number(answers[number])
            is_correct = value == expected
        except Exception:
            is_correct = False
        (correct if is_correct else wrong).append(number)

    lines = [
        f"Correct: {len(correct)} ({', '.join(map(str, correct))})",
        f"Wrong: {len(wrong)} ({', '.join(map(str, wrong))})",
    ]
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return correct, wrong
