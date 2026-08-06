# -*- coding: utf-8 -*-
"""
embedding_demo.py —— 演示"词义 = 向量"：语义相近的词，向量也相近。

原理（对应 PPT 第 2 章）：
  让机器读一堆句子，统计每个词"身边经常出现哪些词"（共现向量）。
  不用人教：上下文相似的词，向量自动就相似了 —— 这就是 embedding 的思想。

运行：python embedding_demo.py   （纯标准库，无需安装任何东西）
"""

from math import sqrt

# ---------- 1. 一个小语料库（已按空格分好词） ----------
# 故意写成"成对换词"的句子：猫/狗、国王/女王、苹果/香蕉、手机/电脑
# 出现的上下文几乎一样 —— 它们的向量应该会自己靠近。
CORPUS = """
猫 喜欢 吃 鱼
狗 喜欢 吃 骨头
我 养 了 一 只 猫
我 养 了 一 只 狗
猫 很 可爱
狗 很 可爱
猫 喜欢 晒 太阳
狗 喜欢 晒 太阳
小猫 喵喵 叫
小狗 汪汪 叫
宠物 猫 在 沙发 上 睡觉
宠物 狗 在 院子 里 玩耍
猫 的 毛 很 软
狗 的 毛 很 软
国王 戴 着 王冠
女王 戴 着 王冠
国王 住 在 王宫 里
女王 住 在 王宫 里
国王 统治 国家
女王 统治 国家
国王 的 权力 很 大
女王 的 权力 很 大
王子 是 国王 的 儿子
公主 是 女王 的 女儿
苹果 是 一 种 水果
香蕉 是 一 种 水果
苹果 很 甜
香蕉 很 甜
我 喜欢 吃 苹果
我 喜欢 吃 香蕉
苹果 可以 榨 果汁
香蕉 可以 做 奶昔
手机 有 一 块 屏幕
电脑 有 一 块 屏幕
我 用 手机 打 电话
我 用 电脑 写 代码
手机 很 智能
电脑 很 智能
手机 需要 充电
电脑 需要 充电
汽车 在 公路 上 行驶
汽车 需要 加油
我 开 汽车 去 上班
汽车 有 四 个 轮子
"""

WINDOW = 2  # 左右各看 2 个词，作为"上下文"


# ---------- 2. 统计共现：每个词 -> {上下文词: 次数} ----------
def build_vectors(corpus, window):
    counts = {}
    for line in corpus.strip().splitlines():
        words = line.split()
        for i, w in enumerate(words):
            vec = counts.setdefault(w, {})
            for j in range(max(0, i - window), min(len(words), i + window + 1)):
                if i != j:
                    ctx = words[j]
                    vec[ctx] = vec.get(ctx, 0) + 1
    return counts


def cosine(v1, v2):
    """余弦相似度：两个向量"方向"有多像（-1 ~ 1，越接近 1 越像）。"""
    dot = sum(v * v2.get(k, 0) for k, v in v1.items())
    n1 = sqrt(sum(v * v for v in v1.values()))
    n2 = sqrt(sum(v * v for v in v2.values()))
    return dot / (n1 * n2) if n1 and n2 else 0.0


def main():
    vectors = build_vectors(CORPUS, WINDOW)

    probes = ["猫", "狗", "国王", "女王", "苹果", "香蕉", "手机", "电脑", "汽车"]

    print("=" * 64)
    print("词义 = 向量：两两相似度（越接近 1 越像，越接近 0 越没关系）")
    print("=" * 64)

    # 打印相似度矩阵
    header = "        " + "".join(f"{w:>8}" for w in probes)
    print(header)
    for w1 in probes:
        row = f"{w1:<6}" + "".join(
            f"{cosine(vectors[w1], vectors[w2]):>8.2f}" for w2 in probes
        )
        print(row)

    # 每个词的"最近邻居"
    print("\n" + "=" * 64)
    print("每个词最像谁？（自动找出的最近邻居）")
    print("=" * 64)
    for w in ["猫", "国王", "苹果", "手机"]:
        sims = sorted(
            ((cosine(vectors[w], vectors[o]), o) for o in vectors if o != w),
            reverse=True,
        )[:3]
        top = "，".join(f"{o}({s:.2f})" for s, o in sims)
        print(f"  {w}  →  {top}")

    print("\n看到了吗：猫-狗、国王-女王、苹果-香蕉、手机-电脑 的分数明显高，")
    print("而 猫-汽车 这种八竿子打不着的组合分数接近 0。")
    print("没有人告诉机器这些词的意思 —— 是它从上下文里自己「凑」出来的。")
    print("真实的 embedding 就是这个思路，只是语料是整个互联网，维度是几百维。")


if __name__ == "__main__":
    main()
