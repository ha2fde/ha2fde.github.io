# -*- coding: utf-8 -*-
"""
第 1 章: 它是不是在搜答案? —— token 切分 + 逐 token 续写
输入: 一句中文(默认 "今天天气真", 可用命令行第一个参数覆盖)
输出: 1) 切分后的 token 列表(id + 文本对照)  2) token 数量  3) 基于前半句的续写结果
运行: python tokenizer_demo.py [你的句子]
依赖: pip install torch transformers   (模型首次运行自动下载, 约 1GB)
国内加速: 取消下面 HF_ENDPOINT 注释, 使用 hf-mirror 镜像
"""
import sys
# import os; os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  # 国内镜像开关
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"   # 续写演示也可用 base 版 "Qwen/Qwen2.5-0.5B"


def main():
    text = sys.argv[1] if len(sys.argv) > 1 else "今天天气真"
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL)

    # ---- 1) 看一句话被切成哪些 token ----
    ids = tok.encode(text)
    print(f"输入: {text}")
    print(f"token 数量: {len(ids)}")
    for i, t in enumerate(ids):
        print(f"  [{i}] id={t:<7} 文本={tok.decode([t])!r}")

    # ---- 2) 给前半句, 看模型逐个 token 续写 ----
    half = text[: max(1, len(text) // 2)]
    inputs = tok(half, return_tensors="pt")
    out = model.generate(**inputs, max_new_tokens=30, do_sample=False)
    print(f"\n前半句: {half!r}")
    print(f"模型续写: {tok.decode(out[0], skip_special_tokens=True)!r}")


if __name__ == "__main__":
    main()
