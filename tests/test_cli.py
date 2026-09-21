"""CLI 与判分流程的端到端测试（需求 1、2、7、8、10）。"""

import os
import tempfile
import unittest

from main import main as app_main


class CliTest(unittest.TestCase):
    def test_generation_writes_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                app_main(["-n", "5", "-r", "10"])
                with open("Exercises.txt", encoding="utf-8") as f:
                    exercises = f.read().splitlines()
                with open("Answers.txt", encoding="utf-8") as f:
                    answers = f.read().splitlines()
            finally:
                os.chdir(original_cwd)

        self.assertEqual(len(exercises), 5)
        self.assertEqual(len(answers), 5)
        for index, (exercise, answer) in enumerate(zip(exercises, answers), 1):
            self.assertEqual(exercise.split(". ", 1)[0], str(index))
            self.assertTrue(exercise.endswith(" ="))
            self.assertEqual(answer.split(". ", 1)[0], str(index))

    def test_missing_r_reports_error_and_help(self):
        # 需求 2：-r 必须给定，否则报错并给出帮助信息
        with self.assertRaises(SystemExit) as ctx:
            app_main(["-n", "10"])
        self.assertEqual(ctx.exception.code, 2)

    def test_grading_outputs_grade_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                with open("Exercises.txt", "w", encoding="utf-8") as f:
                    f.write(
                        "1. 3 + 5 =\n"
                        "2. 1/6 + 1/8 =\n"
                        "3. 2 × 3 =\n"
                        "4. 10 - 4 =\n"
                        "5. 1 ÷ 2 =\n"
                    )
                with open("Answers.txt", "w", encoding="utf-8") as f:
                    f.write(
                        "1. 8\n"
                        "2. 7/24\n"
                        "3. 7\n"   # 错误：应为 6
                        "4. 6\n"
                        "5. 1/2\n"
                    )
                app_main(["-e", "Exercises.txt", "-a", "Answers.txt"])
                with open("Grade.txt", encoding="utf-8") as f:
                    content = f.read()
            finally:
                os.chdir(original_cwd)

        self.assertEqual(
            content,
            "Correct: 4 (1, 2, 4, 5)\nWrong: 1 (3)\n",
        )

    def test_grading_missing_answer_is_wrong(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                with open("Exercises.txt", "w", encoding="utf-8") as f:
                    f.write("1. 3 + 5 =\n2. 4 - 1 =\n")
                with open("Answers.txt", "w", encoding="utf-8") as f:
                    f.write("1. 8\n")  # 缺少第 2 题答案
                app_main(["-e", "Exercises.txt", "-a", "Answers.txt"])
                with open("Grade.txt", encoding="utf-8") as f:
                    content = f.read()
            finally:
                os.chdir(original_cwd)

        self.assertEqual(
            content,
            "Correct: 1 (1)\nWrong: 1 (2)\n",
        )


if __name__ == "__main__":
    unittest.main()
