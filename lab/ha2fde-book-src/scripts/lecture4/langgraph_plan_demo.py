# -*- coding: utf-8 -*-
"""
langgraph_plan_demo.py —— 第7章配套脚本：用 LangGraph 画一张 Plan-and-Execute 图
===================================================================================
把流程画成图，而不是写 if/else：
    START -> plan（规划：任务拆成步骤）-> act（逐步执行）-> sum（汇总答案）-> END
每个节点是一个普通函数，节点间通过 State 共享数据。
运行时会打印节点流转顺序与最终答案。

运行前：pip install langgraph langchain-openai
接口配置：修改下方 CONFIG 区（ChatOpenAI 的 base_url 指向任何兼容接口）
提示：compile() 时传入 checkpointer 即可获得断点恢复/人审，demo 从简。
"""
import operator
from typing import Annotated, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

# ============ CONFIG：在这里配置你的接口 ============
BASE_URL = "https://api.openai.com/v1"   # 或本地服务，如 "http://localhost:11434/v1"
API_KEY = "sk-xxx"
MODEL = "gpt-4o-mini"
# ====================================================

TASK = "估算一家 30 人的远程团队一年的协作软件开销，并给出节省建议。"

llm = ChatOpenAI(base_url=BASE_URL, api_key=API_KEY, model=MODEL, temperature=0)


# ---- State：节点之间共享的数据结构（图的"血液"）----
class PlanState(TypedDict):
    task: str
    plan: list[str]                                # 规划出的步骤
    results: Annotated[list[str], operator.add]    # 各步结果（reducer：追加而非覆盖）
    answer: str


# ---- 节点 1：规划 —— 把任务拆成可执行的步骤列表 ----
def plan_node(state: PlanState):
    print(f"\n[NODE plan] 进入规划，任务：{state['task']}")
    resp = llm.invoke(
        "把任务拆成 3 个有序步骤，每步一行，只输出步骤本身。\n任务：" + state["task"]
    )
    steps = [s.strip() for s in resp.content.strip().splitlines() if s.strip()][:3]
    print(f"[NODE plan] 产出计划：{steps}")
    return {"plan": steps, "results": []}


# ---- 节点 2：执行 —— 逐步完成计划，结果追加进 State ----
def act_node(state: PlanState):
    for i, step in enumerate(state["plan"], 1):
        print(f"\n[NODE act] 执行步骤 {i}/{len(state['plan'])}：{step}")
        resp = llm.invoke(f"执行任务中的一步，给出简洁结果。\n任务：{state['task']}\n步骤：{step}")
        print(f"[NODE act] 步骤 {i} 结果：{resp.content[:80]}...")
        state["results"].append(f"步骤{i}({step})：{resp.content}")
    return {"results": state["results"]}


# ---- 节点 3：汇总 —— 把各步结果合成最终答案 ----
def sum_node(state: PlanState):
    print("\n[NODE sum] 汇总各步结果")
    resp = llm.invoke(
        "把以下各步结果汇总成最终回答。\n" + "\n".join(state["results"])
    )
    return {"answer": resp.content}


def main():
    # ---- 画图：节点是函数，边是流转规则 ----
    g = StateGraph(PlanState)
    g.add_node("plan", plan_node)
    g.add_node("act", act_node)
    g.add_node("sum", sum_node)
    g.add_edge(START, "plan")
    g.add_edge("plan", "act")
    g.add_edge("act", "sum")
    g.add_edge("sum", END)
    app = g.compile()   # 传 checkpointer=... 即获得断点恢复/人审能力

    print("图的流转：START -> plan -> act -> sum -> END")
    final = app.invoke({"task": TASK, "plan": [], "results": [], "answer": ""})
    print("\n" + "=" * 60)
    print("最终答案：\n" + final["answer"])


if __name__ == "__main__":
    main()
