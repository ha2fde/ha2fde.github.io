# -*- coding: utf-8 -*-
"""
第 6 章: 怎么让它知道"没学过"的东西? —— 最小 RAG 演示
输入: 内置 4 段中文资料(报销/考勤/产品/假期) + 一个相关问题(可用命令行参数覆盖)
输出: 1) 切块列表  2) Top-2 检索结果(含相似度)  3) 拼接后的完整 prompt
      4) 模型基于资料的回答
运行: python rag_demo.py [你的问题]
依赖: pip install torch transformers sentence-transformers
模型: BAAI/bge-small-zh-v1.5 (向量, ~100MB) + Qwen/Qwen2.5-0.5B-Instruct (生成)
      不引入向量数据库, 用 numpy 直接算余弦相似度
"""
import sys
import numpy as np
# import os; os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM

EMB_MODEL = "BAAI/bge-small-zh-v1.5"
LLM_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
CHUNK_SIZE = 200   # 每块最多多少字
TOP_K = 2

# ---- 本地资料库(模拟公司内部文档) ----
DOCS = {
    "报销制度.md": (
        "差旅报销标准：员工出差住宿费用，一线城市每晚不超过500元，二线城市每晚不超过400元，"
        "其他城市每晚不超过300元。餐饮补助按自然日计算，每人每天100元。"
        "报销需在出差结束后15个工作日内提交，附发票原件。打车费用仅报销晚于21点的行程。"
    ),
    "考勤规定.md": (
        "公司实行弹性工作制，核心工作时间为上午10点至下午4点，员工需保证每天在岗8小时。"
        "每月允许2次远程办公申请，需提前一天在系统中报备。迟到30分钟以上记为缺勤半天。"
    ),
    "产品手册.md": (
        "旗舰产品X200支持双卡双待，电池容量5000mAh，支持65W快充，"
        "可在30分钟内充电至80%。整机重量189克，提供黑、白、蓝三种配色，质保期24个月。"
    ),
    "假期制度.md": (
        "员工每年享有带薪年假5天起步，每满一年增加1天，上限15天。"
        "年假可拆分使用，最小单位为半天。法定节假日按国家统一安排执行，加班可调休。"
    ),
}


def chunk(text, size):
    """把长文本切成若干小块"""
    return [text[i:i + size] for i in range(0, len(text), size)]


def main():
    question = sys.argv[1] if len(sys.argv) > 1 else "出差住宿报销上限是多少？"

    # ---- 离线: 切块 -> 向量化 -> 存"向量库"(这里就是一个 numpy 数组) ----
    chunks, metas = [], []
    for name, text in DOCS.items():
        for c in chunk(text, CHUNK_SIZE):
            chunks.append(c)
            metas.append(name)
    print(f"共 {len(chunks)} 个块:")
    for i, (c, m) in enumerate(zip(chunks, metas)):
        print(f"  [块{i}] ({m}) {c[:24]}...")

    encoder = SentenceTransformer(EMB_MODEL)
    doc_vecs = encoder.encode(chunks, normalize_embeddings=True)

    # ---- 在线: 问题向量化 -> 相似度检索 Top-K ----
    # bge 中文模型官方建议查询侧加一句检索指令前缀
    q_vec = encoder.encode(["为这个句子生成表示以用于检索相关文章：" + question],
                           normalize_embeddings=True)
    scores = (doc_vecs @ q_vec.T).ravel()
    top_idx = scores.argsort()[::-1][:TOP_K]
    print(f"\n问题: {question}")
    print("Top-2 检索结果:")
    for i in top_idx:
        print(f"  分数={scores[i]:.3f}  ({metas[i]}) {chunks[i][:30]}...")

    # ---- 拼上下文 -> 模型基于资料回答 ----
    context = "\n".join(chunks[i] for i in top_idx)
    prompt = f"资料：\n{context}\n\n问题：{question}\n请根据资料回答，资料没有的信息不要编造。"
    print(f"\n拼接后的 prompt:\n{prompt}")

    tok = AutoTokenizer.from_pretrained(LLM_MODEL)
    model = AutoModelForCausalLM.from_pretrained(LLM_MODEL)
    msgs = [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt")
    out = model.generate(**ids, max_new_tokens=150, do_sample=False)
    answer = tok.decode(out[0][ids.input_ids.shape[1]:], skip_special_tokens=True)
    print(f"\n模型回答: {answer.strip()}")


if __name__ == "__main__":
    main()
