# -*- coding: utf-8 -*-
"""
direct_api_demo.py —— 第2章配套脚本：最底层，直接调 API
=========================================================
只用标准 HTTP 库（requests，非 SDK）调一次 Chat Completions 完成问答，
展示三步：构造 JSON -> POST -> 解析 choices，并打印原始返回。

运行前：pip install requests
接口配置：修改下方 CONFIG 区即可（兼容任何 Chat Completions 接口）
  - 云端：BASE_URL 填官方/代理地址，API_KEY 填你的 Key
  - 本地：BASE_URL 填本地服务地址（如 http://localhost:11434/v1），API_KEY 任意非空串
"""
import json

import requests

# ============ CONFIG：在这里配置你的接口 ============
BASE_URL = "https://api.openai.com/v1"   # 或本地服务，如 "http://localhost:11434/v1"
API_KEY = "sk-xxx"                        # 你的 Key；本地服务可填任意非空串
MODEL = "gpt-4o-mini"                     # 换成你接口支持的模型名
# ====================================================

QUESTION = "用一句话解释：什么是 Agent 的 ReAct 循环？"


def main():
    # 第 1 步：构造请求体 —— Agent 的一切魔法，底层就是这么一个 JSON
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": QUESTION}],
    }

    # 第 2 步：POST 到 Chat Completions 端点
    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()

    # 打印原始返回：看清 API 的真面目（choices / usage / finish_reason ...）
    print("=" * 60)
    print("原始返回 JSON：")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print("=" * 60)

    # 第 3 步：解析 choices[0].message —— 如果有 tool_calls，就该去执行工具了
    msg = data["choices"][0]["message"]
    if msg.get("tool_calls"):
        print("模型想调工具：", msg["tool_calls"])   # 本demo未提供工具，不会走到
    else:
        print("模型回答：", msg["content"])


if __name__ == "__main__":
    main()
