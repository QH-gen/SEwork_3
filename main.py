"""小学四则运算题目自动生成程序 —— 命令行入口。

用法::

    python main.py -n 10 -r 10                  # 生成 10 道 10 以内的题目
    python main.py -e Exercises.txt -a Answers.txt   # 对题目和答案判分
"""

import argparse
import sys

from arithmetic.expr import evaluate, to_string
from arithmetic.generator import QuestionSpaceExhausted, generate_questions
from arithmetic.grader import grade
from arithmetic.numfmt import format_number

EXERCISE_FILE = "Exercises.txt"
ANSWER_FILE = "Answers.txt"
GRADE_FILE = "Grade.txt"


def build_parser():
    parser = argparse.ArgumentParser(
        prog="Myapp",
        description="小学四则运算题目自动生成与判分程序",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python main.py -n 10 -r 10\n"
            "  python main.py -e Exercises.txt -a Answers.txt"
        ),
    )
    parser.add_argument("-n", type=int, default=10, metavar="N",
                        help="生成题目的个数（默认 10）")
    parser.add_argument("-r", type=int, metavar="R",
                        help="题目中数值（自然数、真分数和真分数分母）的范围")
    parser.add_argument("-e", metavar="FILE", help="待判分的题目文件")
    parser.add_argument("-a", metavar="FILE", help="待判分的答案文件")
    return parser


def run_generation(args, parser):
    if args.r is None:
        parser.error("生成题目时必须用 -r 指定数值范围，例如: python main.py -n 10 -r 10")
    if args.r < 1:
        parser.error("-r 必须是正整数")
    if args.n < 1:
        parser.error("-n 必须是正整数")

    try:
        questions = generate_questions(args.n, args.r)
    except QuestionSpaceExhausted as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    with open(EXERCISE_FILE, "w", encoding="utf-8") as f:
        for index, question in enumerate(questions, 1):
            f.write(f"{index}. {to_string(question)} =\n")
    with open(ANSWER_FILE, "w", encoding="utf-8") as f:
        for index, question in enumerate(questions, 1):
            f.write(f"{index}. {format_number(evaluate(question))}\n")

    print(f"已生成 {args.n} 道题目（数值范围 0~{args.r - 1}）:")
    print(f"  题目文件: {EXERCISE_FILE}")
    print(f"  答案文件: {ANSWER_FILE}")
    return 0


def run_grading(args):
    grade(args.e, args.a, GRADE_FILE)
    print(f"判分完成，结果已写入 {GRADE_FILE}")
    return 0


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.e or args.a:
        if not (args.e and args.a):
            parser.error("-e 和 -a 必须同时提供")
        return run_grading(args)
    return run_generation(args, parser)


if __name__ == "__main__":
    sys.exit(main())
