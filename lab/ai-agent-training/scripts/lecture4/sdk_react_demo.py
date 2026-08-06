# -*- coding: utf-8 -*-
"""
sdk_react_demo.py —— 第4章配套脚本：用 SDK 手写 ReAct 循环
=============================================================
用官方 SDK 手写一个 Agent 主循环，内置一个计算器工具。
每轮打印中间过程：模型要调哪个工具 -> 参数是什么 -> 执行结果 -> 回填。
核心结构不到 10 行：发消息+工具描述，有 tool_calls 就执行回填，否则输出。

运行前：pip install openai
接口配置：修改下方 CONFIG 区（base_url 指向任何兼容 Chat Completions 的接口）
"""
import json

from openai import OpenAI

# ============ CONFIG：在这里配置你的接口 ============
BASE_URL = "https://api.openai.com/v1"   # 或本地服务，如 "http://localhost:11434/v1"
API_KEY = "sk-xxx"
MODEL = "gpt-4o-mini"
# ====================================================

TASK = "(128 + 256) * 3 等于多少？算完告诉我结果。"

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)


# ---- 工具 1：计算器（真实执行体）----
def calc(expr: str) -> str:
    try:
        return str(eval(expr, {"__builtins__": {}}, {}))  # demo 用；生产请换安全求值
    except Exception as e:
        return f"计算出错: {e}"


TOOLS = {"calc": calc}

# ---- 工具描述（发给模型的 JSON Schema）----
TOOLS_SCHEMA = [{
    "type": "function",
    "function": {
        "name": "calc",
        "description": "计算一个数学表达式，返回结果字符串",
        "parameters": {
            "type": "object",
            "properties": {"expr": {"type": "string", "description": "如 (128+256)*3"}},
            "required": ["expr"],
        },
    },
}]


def main():
    messages = [{"role": "user", "content": TASK}]
    round_no = 0
    # ============ ReAct 主循环（本脚本唯一的核心） ============
    while True:
        round_no += 1
        print(f"\n----- 第 {round_no} 轮 -----")
        msg = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS_SCHEMA
        ).choices[0].message
        messages.append(msg)

        if not msg.tool_calls:                      # 没有工具调用 -> 想完了
            print("最终回答：", msg.content)
            break

        for c in msg.tool_calls:                    # 想调工具 -> 执行并回填
            args = json.loads(c.function.arguments)
            print(f"模型要调工具: {c.function.name}  参数: {args}")
            result = TOOLS[c.function.name](**args)
            print(f"工具执行结果: {result}  -> 回填 messages")
            messages.append({
                "role": "tool", "tool_call_id": c.id, "content": str(result),
            })
        if round_no >= 8:                           # 安全护栏：轮次上限
            print("超过最大轮次，强制结束")
            break
    # ==========================================================


if __name__ == "__main__":
    main()
