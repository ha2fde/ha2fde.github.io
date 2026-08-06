# -*- coding: utf-8 -*-
"""
第 4 章: 为什么同样的问题, 答案每次不一样? —— temperature / top_p 采样对比
输入: 内置同一问题(可用命令行参数覆盖)
输出: temperature=0(贪心) 与 temperature=0.9(top_p=0.9) 各生成 3 次, 共 6 条结果对比
运行: python sampling_demo.py [你的问题]
依赖: pip install torch transformers
"""
import sys
# import os; os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
N = 3  # 每种设置各生成几次


def main():
    q = sys.argv[1] if len(sys.argv) > 1 else "给我写一句关于秋天的文案"
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL)
    msgs = [{"role": "user", "content": q}]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt")
    print(f"问题: {q}\n")

    configs = [
        ("temperature=0 (贪心, 稳定)", dict(do_sample=False)),
        ("temperature=0.9, top_p=0.9 (发散)", dict(do_sample=True, temperature=0.9, top_p=0.9)),
    ]
    for label, kw in configs:
        print("=" * 25, label, "=" * 25)
        for i in range(1, N + 1):
            out = model.generate(**ids, max_new_tokens=60, **kw)
            ans = tok.decode(out[0][ids.input_ids.shape[1]:], skip_special_tokens=True)
            print(f"[{i}] {ans.strip()}\n")


if __name__ == "__main__":
    main()
