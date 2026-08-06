# -*- coding: utf-8 -*-
"""
第 3 章: 它怎么"记得"我们聊过什么? —— 历史拼接 / 模板渲染 / 超长截断
输入: 内置 6 轮模拟对话(含 system 设定)
输出: 每轮渲染后的模板文本片段 + token 数; 超过上限时演示截断过程:
      system 永远保留, 最老的消息被逐条丢弃
运行: python chat_context_demo.py
依赖: pip install transformers   (本脚本只用 tokenizer, 下载 tokenizer 即可)
"""
# import os; os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from transformers import AutoTokenizer

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
MAX_TOKENS = 180   # 故意调小的"上下文窗口", 方便演示截断

SYSTEM = {"role": "system", "content": "你是简洁的助手，回答不超过两句话。"}

# 模拟一段多轮对话历史( user / assistant 交替 )
ROUNDS = [
    ("我叫小明，是一名后端工程师，平时主要写 Python 和 Go。", "你好小明，很高兴认识你。"),
    ("我最近在研究大模型的上下文管理机制。", "上下文管理是理解对话系统的关键。"),
    ("你能解释一下什么是聊天模板吗？", "聊天模板把消息列表渲染成模型认得的纯文本格式。"),
    ("那上下文窗口超限了怎么办？", "一般会丢弃最老的历史消息，保留最近的对话。"),
    ("我们刚才聊到我叫什么来着？", "你叫小明，是一名后端工程师。"),
    ("今天天气不错，适合出去跑步吗？", "天气好的话跑步很合适，注意补水。"),
]


def render(tok, msgs):
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


def main():
    tok = AutoTokenizer.from_pretrained(MODEL)
    history = []

    for i, (u, a) in enumerate(ROUNDS, 1):
        history.append({"role": "user", "content": u})
        history.append({"role": "assistant", "content": a})

        # ---- 组装: system + 全部历史, 渲染成一段纯文本 ----
        msgs = [SYSTEM] + history
        text = render(tok, msgs)
        n = len(tok(text).input_ids)
        print(f"--- 第 {i} 轮: 当前上下文 {n} tokens ---")

        # ---- 超长截断: 丢最老的历史, system 永不丢 ----
        while n > MAX_TOKENS and history:
            dropped = history.pop(0)
            print(f"  [截断] 丢弃最老消息({dropped['role']}): {dropped['content'][:18]}...")
            msgs = [SYSTEM] + history
            text = render(tok, msgs)
            n = len(tok(text).input_ids)
        print(f"  最终送入模型: {n} tokens, system 保留: {msgs[0] == SYSTEM}")

    # ---- 展示最后一轮模型实际看到的文本(节选) ----
    print("\n=== 模型实际看到的渲染文本(末尾 300 字) ===")
    print(text[-300:])


if __name__ == "__main__":
    main()
