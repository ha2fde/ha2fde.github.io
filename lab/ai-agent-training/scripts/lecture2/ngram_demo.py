# -*- coding: utf-8 -*-
"""
ngram_demo.py —— 演示"统计造句"：n-gram 是怎么学说话的（对应 PPT 第 3 章）。

做法：
  1. 统计文本里"前 N-1 个字之后，最常接哪个字"（数频次，不做任何理解）
  2. 生成时不断查表、按频次抽下一个字 —— 得到"模仿腔"文本

你会看到：腔调很像原文，但细看全是破绽 —— 这就是"只会记词组"的上限。

运行：python ngram_demo.py   （纯标准库，无需安装任何东西）
"""

import random
from collections import defaultdict

# 一段"有腔调"的样本文本（武侠风）。换成任何文本都能模仿。
TEXT = """
江湖夜雨，孤灯如豆。少年仗剑而立，衣袂猎猎作响。远处传来一阵箫声，
箫声幽幽，如泣如诉。少年收剑入鞘，循声而去。山道蜿蜒，松涛阵阵，
一轮冷月悬于绝壁之上。少年抬头望月，忽见一道白影掠过山巅，快如闪电。
少年提气纵身，追了上去。白影忽隐忽现，箫声忽远忽近。少年追到断崖边，
只见云雾翻腾，深不见底。箫声戛然而止。少年仗剑四顾，松风依旧，冷月无声。
"""

N = 3  # 用前 2 个字预测第 3 个字（3-gram）


def train(text, n):
    """统计：前 n-1 个字 -> 下一个字的频次表。"""
    table = defaultdict(lambda: defaultdict(int))
    chars = [c for c in text if not c.isspace()]
    for i in range(len(chars) - n + 1):
        prefix = "".join(chars[i : i + n - 1])
        nxt = chars[i + n - 1]
        table[prefix][nxt] += 1
    return table


def generate(table, n, seed, length=60):
    """从种子开头出发，每次查表、按频次随机抽下一个字。"""
    out = list(seed)
    for _ in range(length):
        prefix = "".join(out[-(n - 1):])
        candidates = table.get(prefix)
        if not candidates:  # 表里没有这个前文 —— 抓瞎，随机挑一个字续命
            nxt = random.choice(list("的一是不了我人在他有上"))
        else:
            chars, weights = zip(*candidates.items())
            nxt = random.choices(chars, weights=weights)[0]
        out.append(nxt)
    return "".join(out)


def main():
    random.seed(42)
    table = train(TEXT, N)

    print("=" * 64)
    print(f"第 1 步：统计表长这样（{N-1} 个字 -> 下一个字的频次）")
    print("=" * 64)
    for prefix in ["少年仗", "年仗剑", "箫声", "月"]:
        key = prefix[-(N - 1):]
        if key in table:
            items = sorted(table[key].items(), key=lambda kv: -kv[1])
            top = "  ".join(f"{c}×{n}" for c, n in items[:5])
            print(f"  「{key}」之后接过 → {top}")

    print("\n" + "=" * 64)
    print("第 2 步：查表生成 3 段「模仿腔」文本")
    print("=" * 64)
    for i, seed in enumerate(["少年仗剑", "箫声幽幽", "冷月无声"], 1):
        print(f"\n【生成 {i}】（开头：{seed}）")
        print("  " + generate(table, N, seed))

    print("\n" + "=" * 64)
    print("观察：字都是原文里的字，腔调也像 —— 但句子讲不通。")
    print("这就是 n-gram 的天花板：只会「背词组」，从不「懂意思」。")
    print("而且换一段它没背过的前文，它就只能瞎接。")


if __name__ == "__main__":
    main()
