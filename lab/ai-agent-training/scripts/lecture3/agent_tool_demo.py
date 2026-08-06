# -*- coding: utf-8 -*-
"""
第 7 章: 怎么让它"动手干活"? —— 工具调用 + ReAct 循环
输入: 需要计算的提问(默认 "38乘27再加100是多少?", 可用命令行参数覆盖)
输出: 每轮 Thought / Action / Observation 日志 + 最终回答
运行: python agent_tool_demo.py [你的问题]
依赖: pip install torch transformers
原理: 工具说明写进提示词 -> 模型输出 "Action: 工具(参数)" 或 "Final: 答案"
      -> 程序解析并真正执行 -> 结果以 role=tool 回填 -> 继续循环, 上限 5 轮
说明: 0.5B 小模型不一定每次都遵守格式, 脚本带解析失败兜底; 换更大模型更稳
"""
import sys
import ast
import operator as op
import datetime
# import os; os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
MAX_LOOPS = 5

# ---------------- 工具实现(程序真正执行的部分) ----------------
_OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
        ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod, ast.USub: op.neg}


def safe_eval(expr):
    """只允许四则运算/乘方/取余的安全计算器(不用 eval)"""
    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.operand))
        raise ValueError(f"不支持的表达式: {ast.dump(node)}")
    return ev(ast.parse(expr, mode="eval"))


def calc(expr: str) -> str:
    try:
        return str(safe_eval(expr))
    except Exception as e:
        return f"计算失败: {e}"


def current_date() -> str:
    return datetime.date.today().isoformat()


TOOLS = {"calc": calc, "current_date": current_date}

SYSTEM_PROMPT = """你是一个会使用工具的助手。可用工具：
- calc(expr): 计算器，计算数学表达式，如 calc(38*27+100)
- current_date(): 返回今天的日期

工作方式：每一步你只能输出以下两种格式之一：
1) 需要工具时输出一行： Action: 工具名(参数)
2) 信息足够回答时输出一行： Final: 你的最终答案
不要输出其他内容。"""


def llm(tok, model, messages):
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt")
    out = model.generate(**ids, max_new_tokens=120, do_sample=False)
    return tok.decode(out[0][ids.input_ids.shape[1]:], skip_special_tokens=True).strip()


def parse_action(out):
    """从模型输出中解析 Action: name(args), 解析不到返回 None"""
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("Action:"):
            call = line[len("Action:"):].strip()
            name, _, rest = call.partition("(")
            args = rest.rsplit(")", 1)[0].strip().strip("'\"")
            return name.strip(), args
    return None


def main():
    question = sys.argv[1] if len(sys.argv) > 1 else "38乘27再加100是多少？"
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    print(f"问题: {question}\n")

    # ---------------- ReAct 主循环 ----------------
    for step in range(1, MAX_LOOPS + 1):
        out = llm(tok, model, messages)            # Thought
        print(f"--- 第 {step} 轮 ---")
        print(f"模型输出: {out}")

        if "Final:" in out:                      # 决定直接回答
            print(f"\n最终回答: {out.split('Final:')[-1].strip()}")
            return

        parsed = parse_action(out)               # 解析 Action
        if parsed is None:
            print("未解析到 Action, 要求模型按格式重试")
            messages.append({"role": "assistant", "content": out})
            messages.append({"role": "user", "content":
                             "请严格按格式输出: Action: 工具名(参数) 或 Final: 答案"})
            continue

        name, args = parsed
        if name not in TOOLS:
            result = f"未知工具: {name}"
        else:
            result = TOOLS[name](args) if args else TOOLS[name]()
        print(f"执行工具: {name}({args}) -> {result}")

        # Observation: 结果以 role=tool 回填进上下文
        messages.append({"role": "assistant", "content": out})
        messages.append({"role": "tool", "content": f"Observation: {result}"})

    print("\n达到循环上限, 强制结束(防止死循环)")


if __name__ == "__main__":
    main()
