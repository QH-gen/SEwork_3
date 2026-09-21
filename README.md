# 小学四则运算自动生成程序

命令行程序：自动生成满足约束的小学四则运算题目，计算答案，并对给定的题目/答案文件判分。

- 邓子豪 3124004165
- 黄琪 3124004169

## 运行环境

- Python 3.8+（仅使用标准库，无需安装第三方依赖）

## 使用方法

### 生成题目

```bash
python main.py -n 10 -r 10
```

- `-n`：生成题目的个数（默认 10）
- `-r`：题目中数值（自然数、真分数和真分数分母）的范围，**必须给定**，
  数值取 0 ~ r-1；缺失时程序报错并打印帮助信息

生成的题目写入当前目录的 `Exercises.txt`，对应答案写入 `Answers.txt`：

```
1. 3 + 5 =
2. 1/6 + 1/8 =
...
```

```
1. 8
2. 7/24
...
```

真分数的格式：五分之三写作 `3/5`，二又八分之三写作 `2'3/8`。

### 判分

```bash
python main.py -e Exercises.txt -a Answers.txt
```

判定答案对错并统计数量，结果写入当前目录的 `Grade.txt`：

```
Correct: 5 (1, 3, 5, 7, 9)
Wrong: 5 (2, 4, 6, 8, 10)
```

### 查看帮助

```bash
python main.py -h
```

## 题目约束

1. 计算过程不产生负数（`e1 - e2` 满足 `e1 >= e2`）
2. 除法子表达式 `e1 ÷ e2` 的商是真分数（`0 < e1/e2 < 1`）
3. 每道题目运算符个数 1 ~ 3 个
4. 一次运行内的题目互不重复（以 `+`/`×` 左右交换为等价标准的规范化判重）
5. 支持一次生成一万道题目（`python main.py -n 10000 -r 50`）

## 运行测试

```bash
python -m unittest discover -s . -p "test_*.py" -v
```

## 效能分析

```bash
python profile_gen.py           # 默认 -n 10000 -r 50
python profile_gen.py 5000 20   # 自定义规模
```

## 项目结构

```
main.py                 命令行入口（参数解析、模式分发）
profile_gen.py          cProfile 效能分析脚本
arithmetic/
    numfmt.py           数值格式化/解析（自然数、真分数、带分数）
    expr.py             表达式树：求值、约束检查、序列化、规范化判重
    parser.py           题目字符串 → 表达式树（递归下降）
    generator.py        随机生成满足约束且互不重复的题目
    grader.py           判分，输出 Grade.txt
tests/                  单元测试（unittest）
docs/博文素材.md         博客所需的 PSP 表格、效能分析、设计说明等
```
