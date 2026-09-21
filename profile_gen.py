"""效能分析脚本：用 cProfile 统计生成 10000 道题目（需求 9）的耗时分布。

用法::

    python profile_gen.py            # 默认 -n 10000 -r 50
    python profile_gen.py 5000 20
"""

import cProfile
import pstats
import random
import sys
import time

from arithmetic.generator import generate_questions


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    value_range = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    profiler = cProfile.Profile()
    start = time.perf_counter()
    profiler.enable()
    questions = generate_questions(count, value_range, rng=random.Random(42))
    profiler.disable()
    elapsed = time.perf_counter() - start

    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative").print_stats(15)
    print(f"共生成 {len(questions)} 道题目（-n {count} -r {value_range}），"
          f"总耗时 {elapsed:.2f} 秒")


if __name__ == "__main__":
    main()
