# -*- coding: utf-8 -*-
"""
第 2 章: 它凭什么会"回答问题"? —— base 模型 vs chat 模型同题对比
输入: 内置同一问题(可用命令行参数覆盖)
输出: base 模型的"续写"结果 与 instruct 模型的"问答"结果, 并排打印
运行: python training_stages_demo.py [你的问题]
依赖: pip install torch transformers
说明: base 版约 1GB, instruct 版约 1GB, 首次运行自动下载
      base 不套聊天模板(直接续写原文), instruct 走 apply_chat_template
"""
import sys
# import os; os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from transformers import AutoTokenizer, AutoModelForCausalLM

BASE = "Qwen/Qwen2.5-0.5B"            # 只做预训练: 会续写, 不会对话
CHAT = "Qwen/Qwen2.5-0.5B-Instruct"   # 预训练 + SFT + 对齐: 会回答问题


def gen(model_name, prompt, use_template):
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    if use_template:
        msgs = [{"role": "user", "content": prompt}]
        prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    ids = tok(prompt, return_tensors="pt")
    out = model.generate(**ids, max_new_tokens=80, do_sample=False)
    return tok.decode(out[0][ids.input_ids.shape[1]:], skip_special_tokens=True)


def main():
    q = sys.argv[1] if len(sys.argv) > 1 else "怎么煮咖啡?"
    print(f"问题: {q}\n")
    print("=" * 20, "base 模型(只预训练)", "=" * 20)
    print(gen(BASE, q, use_template=False))
    print("\n" + "=" * 20, "chat 模型(+SFT+对齐)", "=" * 20)
    print(gen(CHAT, q, use_template=True))


if __name__ == "__main__":
    main()
