# -*- coding: utf-8 -*-
"""
第 5 章: 为什么它会一本正经地胡说八道? —— 思维链 CoT 对比
输入: 内置一道多步算术题(可用命令行参数覆盖)
输出: "直接给出答案" 与 "请一步一步思考" 两种提示的输出对比
运行: python cot_demo.py [你的题目]
依赖: pip install torch transformers
说明: 0.5B 小模型能力有限, 重点演示提示法的结构差异;
      把 MODEL 换成 Qwen/Qwen2.5-1.5B-Instruct 或更大, 效果对比会更明显
"""
import sys
# import os; os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"


def ask(tok, model, prompt):
    msgs = [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt")
    out = model.generate(**ids, max_new_tokens=200, do_sample=False)
    return tok.decode(out[0][ids.input_ids.shape[1]:], skip_special_tokens=True).strip()


def main():
    q = sys.argv[1] if len(sys.argv) > 1 else "3个人4天摘了72千克苹果，平均每人每天摘多少千克？"
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL)
    print(f"题目: {q}\n")

    print("=" * 22, "提示一: 直接回答", "=" * 22)
    print(ask(tok, model, f"{q}\n直接给出答案。"))

    print("\n" + "=" * 22, "提示二: 逐步思考(CoT)", "=" * 22)
    print(ask(tok, model, f"{q}\n请一步一步思考，再给出答案。"))

    print("\n(正确答案: 72 / 4 / 3 = 6 千克)")


if __name__ == "__main__":
    main()
