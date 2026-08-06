# -*- coding: utf-8 -*-
"""
tiny_lm_train_demo.py —— 亲手训练一个极小的语言模型（对应 PPT 第 3~9 章）。

它做的事情，和训练 GPT 在结构上一模一样：
  1. 任务：给定前面几个字，预测下一个字（语言模型的主线任务）
  2. 模型：字 -> 向量(embedding) -> 若干层加权变换 -> 每个候选字的概率
  3. 训练：预测错了就算"错多少"(loss)，再微调权重，重复几千次
  4. 看 loss 一路下降，再让它续写 —— 从乱码长成"有点像"

规模：约 4 万个参数（GPT 是千亿级，但流程相同），普通 CPU 几秒跑完。

运行：python tiny_lm_train_demo.py   （需要 numpy：pip install numpy）
"""

import numpy as np

# ---------- 训练文本：几首古诗（字符级建模，字就是"词"） ----------
TEXT = """
床前明月光，疑是地上霜。举头望明月，低头思故乡。
春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。
白日依山尽，黄河入海流。欲穷千里目，更上一层楼。
红豆生南国，春来发几枝。愿君多采撷，此物最相思。
空山不见人，但闻人语响。返景入深林，复照青苔上。
千山鸟飞绝，万径人踪灭。孤舟蓑笠翁，独钓寒江雪。
"""

CTX = 8     # 用前 8 个字预测下一个字
DIM = 24    # 每个字的向量维度（embedding）
HID = 128   # 隐藏层大小
STEPS = 3000
BATCH = 32
LR = 0.3

rng = np.random.default_rng(42)

# ---------- 字表 ----------
chars = sorted(set(TEXT))
V = len(chars)
c2i = {c: i for i, c in enumerate(chars)}
i2c = dict(enumerate(chars))
data = np.array([c2i[c] for c in TEXT])

# ---------- 模型参数（随机初始化） ----------
E = rng.normal(0, 0.1, (V, DIM))            # 字向量表
W1 = rng.normal(0, 0.1, (CTX * DIM, HID))   # 隐藏层权重
b1 = np.zeros(HID)
W2 = rng.normal(0, 0.1, (HID, V))           # 输出层权重
b2 = np.zeros(V)

n_params = sum(p.size for p in [E, W1, b1, W2, b2])
print(f"字表大小 {V}，模型参数 {n_params:,} 个（GPT 是千亿级，流程相同）\n")


def forward(X):
    """X: (batch, CTX) 个字 -> 每个候选字的概率。"""
    emb = E[X].reshape(len(X), -1)       # 字 -> 向量，拼成一长条
    h = np.tanh(emb @ W1 + b1)           # 一层加权变换
    z = h @ W2 + b2                      # 再一层 -> 每个候选字的得分
    z -= z.max(axis=1, keepdims=True)    # 数值稳定
    p = np.exp(z)
    p /= p.sum(axis=1, keepdims=True)    # 得分 -> 概率
    return emb, h, p


def sample_batch():
    ix = rng.integers(CTX, len(data), size=BATCH)
    X = np.stack([data[i - CTX : i] for i in ix])
    return X, data[ix]


# ---------- 生成：给它一个开头，让它自己往下续 ----------
def generate(seed_text, length=40, temperature=0.8):
    ctx = ([0] * CTX + [c2i.get(c, 0) for c in seed_text])[-CTX:]  # 不足 8 个字前面补 0
    out = list(seed_text)
    for _ in range(length):
        X = np.array([ctx[-CTX:]])
        _, _, p = forward(X)
        p = p[0] ** (1 / temperature)
        p /= p.sum()
        nxt = rng.choice(V, p=p)
        out.append(i2c[nxt])
        ctx.append(nxt)
    return "".join(out)


# ---------- 训练前：模型还是"白纸"，续写是乱码 ----------
print("【训练前】让它续写「床前明月光」—— 纯随机，是乱码：")
print("   " + generate("床前明月光", 20) + "\n")

# ---------- 训练：就是不断重复"预测 -> 算错多少 -> 微调权重" ----------
print("开始训练（训练 = 不断把预测错误往下压）：")
for step in range(1, STEPS + 1):
    X, Y = sample_batch()
    emb, h, p = forward(X)

    loss = -np.log(p[np.arange(len(X)), Y]).mean()   # 预测错多少

    # 反向算"每个参数该往哪调"（梯度），再微调
    dz = p
    dz[np.arange(len(X)), Y] -= 1      # 正确答案那一维，误差最大
    dz /= len(X)
    dW2, db2 = h.T @ dz, dz.sum(axis=0)
    dh = (dz @ W2.T) * (1 - h**2)
    dW1, db1 = emb.T @ dh, dh.sum(axis=0)
    demb = (dh @ W1.T).reshape(len(X), CTX, DIM)

    for param, grad in [(W1, dW1), (b1, db1), (W2, dW2), (b2, db2)]:
        param -= LR * grad             # 错了就微调权重
    np.add.at(E, X, -LR * demb)        # 字向量表也一样微调

    if step % 500 == 0 or step == 1:
        print(f"  第 {step:>5} 步   loss = {loss:.3f}")


print("\n【训练后】再让它续写几句（开头是我们给的，后面全是它自己接的）：")
for seed in ["床前明月光", "春眠不觉晓", "白日依山尽", "千山鸟飞绝"]:
    print(f"\n  【{seed} ……】")
    print("   " + generate(seed))

print("\n看到了吗：")
print("  · loss 一路下降 —— “训练”就是在压这个预测错误；")
print("  · 生成的字从乱码变成了有诗的样子 —— 规律是从数据里学出来的，没人教它；")
print("  · 把模型放大到千亿参数、文本换成整个互联网 —— 那就是 GPT 的预训练。")
