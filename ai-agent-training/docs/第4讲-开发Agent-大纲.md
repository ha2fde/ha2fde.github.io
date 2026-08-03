# 《开发 Agent：从直接调 API 到用框架编排》PPT 大纲 v1

- 受众：懂基本 IT、了解 Agent 原理（ReAct、工具调用）的开发者
- 定位：「懂原理 → 能开发」落地篇
- 核心叙事：开发 Agent = 不断做「抽象降级」——从手拼 HTTP 到框架里画图，每层减少重复劳动、增加框架依赖
- 总页数：19 页（第 8 章 3 页，第 1/6/9 章各 2 页，其余 1~2 页）
- 每章固定四块：① 你可能的疑惑 → ② 关键差异点破 → ③ ASCII 架构图 → ④ 右下角主干代码（≤8 行）
- 深度标尺：每个机制让读者能用一句话说清「它解决什么、什么场景用它」

---

## P1｜封面

**开发 Agent：从直接调 API 到用框架编排**
副标题：三条路线、两种范式、一张选型地图
定位语：你已经懂 Agent 原理了——这一篇只解决「代码怎么写、框架怎么选」

---

## P2｜导读：整篇只有一条主线

**你可能的疑惑**：原理我都懂，一搜「怎么开发 Agent」，出来几十个框架，从哪下手？

**关键差异**：选型的本质不是「哪个框架好」，而是「我愿意把多少控制权交给框架换多少省力」。

```
一条主线：抽象降级（省力的每一步，都在交出一点控制权）

  手拼 HTTP 请求  ──►  官方 SDK  ──►  手写循环  ──►  框架执行器  ──►  图编排
  (完全掌控)        (省样板)      (流程自写)     (循环现成)      (流程即图)

  ◄──────────── 控制力递减 │ 省力递增 │ 框架依赖递增 ────────────►
```

页面要点：
- 本篇地图：路线（API/SDK/框架）→ 范式（ReAct / Plan-and-Execute）→ 选型（四组框架 + 决策树）→ 实战步骤
- 附 3 个可运行脚本：同一能力，三层写法

---

## 第 1 章　懂原理了，代码怎么写？（2 页）

### P3｜1-1 三条路线总览

**你可能的疑惑**：调个大模型而已，为什么有「裸调 API / 用 SDK / 上框架」三种写法？

**关键差异**：三条路线不是替代关系，是光谱——差别只在「样板代码谁写、循环谁管、状态谁存」。

| 路线 | 帮你解决 | 你要付出的代价 |
|---|---|---|
| 直接调 API | 零依赖、完全掌控、任何语言都能写 | 请求体、tool_calls 解析、循环、重试全自己写 |
| 官方 SDK | 流式/重试/类型/鉴权开箱即用 | 「流程」（循环+回填）仍要自己写 |
| Agent 框架 | 循环执行器、工具管理、记忆、人审现成 | 学框架的世界观，被其抽象绑定 |

### P4｜1-2 抽象光谱图（本章记忆点）

```
抽象程度 低 ────────────────────────────────────────► 高

  直接调 HTTP API        官方 SDK             Agent 框架
 ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐
 │ 手拼 JSON 请求体 │  │ client.chat.     │  │ 声明工具 + 画图/链   │
 │ 手解 tool_calls │  │ completions.     │  │ 循环执行器现成       │
 │ 手写 while 循环 │  │ create(...)      │  │ 断点/人审/回放       │
 └────────────────┘  └────────────────┘  └────────────────────┘
  掌控力 ★★★★★         掌控力 ★★★★          掌控力 ★★★
  样板：全自己写        样板：省一半          样板：≈ 0
  依赖：一个 HTTP 库    依赖：官方 SDK       依赖：框架及其世界观
```

**一句话**：没有「该用哪个」，只有「这个任务值得我交出多少控制权」。

---

## 第 2 章　最底层：直接调 API（1 页）

### P5｜手拼请求体 + 手解返回

**你可能的疑惑**：框架里神秘的 Agent，底层到底在干嘛？

**关键差异**：底层只有一次普通 POST——把 `messages + tools` 塞进请求体，从返回里找 `tool_calls`。Agent 的一切魔法都是围绕这次 POST 的封装。

```
你的程序                          大模型 API
   │  POST /chat/completions         │
   │  { messages: [...历史...],      │
   │    tools:    [...工具描述...] } ─►│
   │                                 │ 模型决定：直接答 or 调工具
   │  ◄─ choices[0].message ─────────│
   │     ├ 有 tool_calls → 你执行工具，结果塞回 messages，再 POST
   │     └ 无 tool_calls → content 就是答案
```

主干代码（≤8 行）：

```python
import requests
resp = requests.post(f"{BASE_URL}/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"model": MODEL, "messages": messages, "tools": tools})
msg = resp.json()["choices"][0]["message"]
if msg.get("tool_calls"):   # 解析、执行、回填、再请求：全靠自己
    ...
```

优点：完全掌控、零抽象、调试所见即所得。缺点：样板代码（循环/重试/流式/并发）全自己写。
**什么时候用它**：一次调用的简单任务、学习原理、框架不适配的边缘场景。

---

## 第 3 章　SDK 帮你省什么（1 页）

### P6｜SDK = 把「通信杂务」收走，但「流程」还是你的

**你可能的疑惑**：SDK 和裸调 API 相比，到底省了什么？是不是 SDK 就能跑 Agent 了？

**关键差异**：SDK 只封装「怎么跟模型说话」（请求/流式/重试/类型），不封装「怎么思考」（循环与回填）——后者仍是你的代码。

```
裸调 API 你要管的：                SDK 帮你管掉的：
 ├ 拼 JSON / 拼 header    ──►     ├ client.chat.completions.create()
 ├ 鉴权、超时、重试       ──►     ├ 内置重试与超时
 ├ SSE 流式解析           ──►     ├ stream=True 迭代器
 ├ 返回 JSON 反序列化      ──►     ├ 类型化对象（msg.tool_calls）
 └ 手写 Agent 循环         ✖ 仍归你  ← SDK 不管「流程」
```

主干代码（≤8 行）：

```python
from openai import OpenAI
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)   # 换 base_url 即可接本地/云端
resp = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
msg = resp.choices[0].message
if msg.tool_calls: ...        # 流程仍自己写 → 下一章
```

**一句话**：SDK 省的是「通信样板」，不是「Agent 流程」。从 SDK 到 Agent，只差一个你亲手写的循环。

---

## 第 4 章　手写一个 Agent（1~2 页）

### P7｜ReAct 主循环：核心结构就这几行

**你可能的疑惑**：ReAct 听懂了，写成代码长什么样？

**关键差异**：所谓 Agent，本质就是「发消息+工具描述 → 有工具调用就执行回填，没有就输出」的 while 循环。全部秘密在 messages 的追加方式。

```
        ┌─────────────────── ReAct 循环 ───────────────────┐
        │                                                  │
        ▼                                                  │
 [messages] → [LLM 推理：回答 or 调工具?] → 有 tool_calls? ─是→ [执行工具函数]
                     ▲                                     │结果以 role="tool"
                     │                                     │追加回 messages
                     └─────────────────────────────────────┘
                     否（没有 tool_calls）
                     ▼
              [输出最终回答，循环结束]
```

主干代码（≤8 行，完整可跑版见附录脚本 2）：

```python
messages = [{"role": "user", "content": task}]
while True:
    msg = client.chat.completions.create(model=MODEL, messages=messages, tools=tools).choices[0].message
    messages.append(msg)
    if not msg.tool_calls: return msg.content          # 想完了 → 输出
    for c in msg.tool_calls:                           # 想调用 → 执行
        r = TOOLS[c.function.name](**json.loads(c.function.arguments))
        messages.append({"role": "tool", "tool_call_id": c.id, "content": str(r)})
```

调试要点（演讲中强调）：每轮打印「模型要调哪个工具 → 参数 → 回填结果」，中间过程全可见。
（如版面允许可拆 2 页：P7a 结构图，P7b 代码 + 执行轨迹示例）

---

## 第 5 章　框架化的通用 ReAct（1 页）

### P8｜声明工具即可：从 20 行到 5 行

**你可能的疑惑**：既然循环是固定的，为什么每个项目都要重抄一遍？

**关键差异**：框架把第 4 章那个「谁都一样」的循环收走了——你只声明「模型是谁、工具有哪些」，循环、回填、异常处理全由执行器包办。

```
第4章（手写）                       第5章（框架执行器）
┌───────────────────────┐        ┌────────────────────────┐
│ while True:            │        │ agent = create_react_  │
│   请求 LLM             │  ──►   │   agent(model, tools)  │
│   解析 tool_calls      │        │ agent.invoke(task)     │
│   查表执行工具          │        │                        │
│   拼 role="tool" 回填   │        │ 循环/回填/异常：框架全包  │
│   判断结束条件          │        │                        │
└───────────────────────┘        └────────────────────────┘
        ~20 行                            ~5 行
```

主干代码（≤5 行）：

```python
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(model, tools=[calc])      # 声明工具即可
result = agent.invoke({"messages": [("user", "12*(3+4) 是多少？")]})
```

**一句话**：框架第一层价值 = 通用 ReAct 执行器。代价：行为细节藏在框架里，调试要学会看它的日志。

---

## 第 6 章　更复杂的任务：两种流程范式（2 页）

### P9｜6-1 ReAct vs Plan-and-Execute：机制对比

**你可能的疑惑**：任务一复杂，ReAct 就「走一步看一步」走到迷路，怎么办？

**关键差异**：ReAct 把计划藏在模型脑子里（边想边做）；Plan-and-Execute 把计划变成显式对象（先整体规划，再逐步执行，偏了可重规划）。

```
ReAct（边想边做）                    Plan-and-Execute（先谋后动）

 想→做→看→想→做→看→答               ①规划：任务→[步骤1,步骤2,步骤3]
 每一步由最新观察决定                ②执行：步1✓→步2✓→ 结果偏离?
 计划不可见，随时可变                ③重规划：改计划→步2'→步3✓
 适合：探索型、路径未知              ④汇总：各步结果→最终答案
 例：排查故障、开放式调研            适合：可预分解的多步任务
                                    例：写报告、多源数据汇总
```

### P10｜6-2 场景对照表（该选哪个）

| 维度 | ReAct | Plan-and-Execute |
|---|---|---|
| 思考方式 | 边想边做，计划隐式 | 先谋后动，计划显式 |
| 计划可修正性 | 每步天然可变 | 通过「重规划」节点显式修正 |
| Token 消耗 | 每轮带全历史，较高 | 规划一次，执行步骤间可精简 |
| 适合任务 | 探索型、步骤不可预知 | 可预分解、步骤间有依赖 |
| 典型风险 | 绕圈、跑偏不自知 | 计划错了执行全错（需重规划兜底） |
| 一句话 | 「走一步看一步」 | 「先画地图再上路」 |

**一句话**：先问自己「任务的步骤在出发前能不能列出来」——能列用 Plan，列不出用 ReAct，真实系统常混用。

---

## 第 7 章　LangGraph：把流程画成图（1~2 页）

### P11｜Node / Edge / State：流程从 if/else 变成图

**你可能的疑惑**：范式一多、分支一多，while 里全是 if/else，怎么管？

**关键差异**：LangGraph 不再用 if/else 描述流程，而是把流程声明成图——节点是函数，边是流转规则，State 是节点间共享的数据。图一旦显式化，断点恢复、回放、人审就是免费的。

```
if/else 写法（流程埋在代码里）        LangGraph 写法（流程是显式的图）

while True:                          ┌─► plan ──► act ──► sum ─► END
  if 该规划: ...                     │           │  ▲
  elif 该执行: ...                   START       └──┘ 条件边
  elif 该问人: interrupt(...)        └─ (执行偏了→回 plan 重规划)
  else: break                        State = {task, plan[], results[], answer}
流程 = 你脑补出来的                   流程 = 画出来的，可看、可断、可回放
```

主干代码（≤8 行）：

```python
g = StateGraph(AgentState)
g.add_node("plan", plan_node); g.add_node("act", act_node); g.add_node("sum", sum_node)
g.add_edge(START, "plan"); g.add_edge("plan", "act"); g.add_edge("act", "sum")
app = g.compile(checkpointer=MemorySaver())     # 断点恢复：一行的事
app.invoke({"task": task}, config={"configurable": {"thread_id": "demo-1"}})
```

图 vs if/else 的收益：断点恢复（checkpointer）、执行可回放、人审（interrupt）、可视化排错。
（完整 Plan-and-Execute 示例见附录脚本 3）

---

## 第 8 章　框架全景与怎么选（3 页，重头戏）

### P12｜8-1 四组框架分组图（先分组，再比较）

**你可能的疑惑**：框架这么多，难道要一个个学？

**关键差异**：先按「定位」分四组——组内差异小，组间差异大；选型先选组，再选个。

```
① 图编排组（灵活可控）        ② 工具箱/开箱即用组（上手快）
   LangGraph   状态图，复杂流程+人审    LangChain   工具链+预置执行器，生态大但抽象多
   PydanticAI  类型安全，输出结构化     LlamaIndex  以数据/RAG 为主
                                       CrewAI      多智能体，角色分工
                                       AutoGen     多智能体，对话协作

③ 官方轻量组（快速验证）       ④ 低代码/生态绑定组（给人用/跟栈走）
   OpenAI Agents SDK  官方，function    Dify            可视化编排，非开发者友好
                      calling 快速验证   Semantic Kernel 微软系，.NET/企业集成
   smolagents         HF 出品，轻量     Vercel AI SDK   JS/TS，前端 Web 流式 UI
```

读法：横向是「控制力→省力」，纵向是「通用→专用/生态」。

### P13｜8-2 总对比表（仅此一张表，6 列）

| 框架 | 定位 | 语言 | 核心抽象 | 上手难度 | 最擅长场景 | 何时不建议用 |
|---|---|---|---|---|---|---|
| LangGraph | 图编排 | Python | 状态图 Node/Edge/State | 中 | 复杂流程、人审、断点恢复 | 一次调用的简单任务 |
| PydanticAI | 图编排·类型安全 | Python | 类型化 Agent + 依赖注入 | 中低 | 结构化输出、生产级单 Agent | 需要复杂多步图编排 |
| LangChain | 工具箱 | Python/JS | Chain + 预置执行器 | 低→中 | 快速拼装、生态集成 | 厌恶层层抽象、要精细控制 |
| LlamaIndex | 数据/RAG | Python | 索引 + 检索器 | 低 | 知识库问答、RAG 占比高 | 工具调用为主的通用 Agent |
| CrewAI | 多智能体 | Python | 角色 + 任务 + Crew | 低 | 角色分工明确的协作 | 单 Agent 就够的任务 |
| AutoGen | 多智能体 | Python | 对话驱动的 Agent 群 | 中 | 研究型多 Agent 讨论 | 要确定性流程的生产环境 |
| OpenAI Agents SDK | 官方轻量 | Python | Agent + Handoff | 低 | function calling 快速验证 | 以非 OpenAI 模型为主 |
| smolagents | 官方轻量 | Python | CodeAgent（代码即动作） | 低 | 轻量实验、HF 生态 | 企业级复杂编排 |
| Dify | 低代码 | Web 可视化 | 画布 + 节点 | 极低 | 非开发者、快速上线产品 | 需要深度定制逻辑 |
| Semantic Kernel | 企业/微软系 | .NET/Python | Planner + Plugin | 中 | 企业集成、.NET 技术栈 | 轻量快速原型 |
| Vercel AI SDK | 前端生态 | JS/TS | Hooks + 流式 UI | 低 | Web 聊天界面、全栈 JS | 后端重型流程编排 |

### P14｜8-3 选型决策树（按维度逐层分流）

```
Q0 一次调用就能搞定？
 ├─ 是 → 直接调 API / SDK 就够了，别上框架
 └─ 否 → Q1 需要人审 / 断点恢复 / 可回放吗？
      ├─ 需要 → LangGraph（图编排，控制最强）
      └─ 不需要 → Q2 是多智能体协作吗？
           ├─ 是 → 角色分工明确→CrewAI ｜ 自由讨论→AutoGen
           └─ 否 → Q3 技术栈/场景？
                ├─ .NET / 企业集成 → Semantic Kernel
                ├─ JS/TS / 前端 Web → Vercel AI SDK
                ├─ 数据/RAG 占比高  → LlamaIndex
                ├─ 要类型安全/结构化输出 → PydanticAI
                ├─ 只想快速验证 → OpenAI Agents SDK / smolagents
                └─ Q4 要给非开发者用？→ Dify（可视化编排）
```

口诀预告：简单用 API，多步用图，要给人用选 Dify。

---

## 第 9 章　同一个任务，两种写法（2 页）

### P15｜9-1 「算数 + 查词义」：SDK 手写 vs LangGraph 图编排

**你可能的疑惑**：同一个任务，两种写法的代码结构到底差在哪？

**关键差异**：SDK 手写 = 流程控制在你手里（循环+if/else）；LangGraph = 你只写节点函数，流转由图接管。任务越复杂，差异越值回票价。

```
任务：算出 23*47，再查「结果」一词的英文释义，合并回答

SDK 手写（流程在你代码里）            LangGraph（流程在图里）
┌──────────────────────────┐        START
├ while 循环                │         ▼
│   ├ LLM 决定下一步        │      ┌ router（LLM 决定去哪）
│   ├ if 要算数 → calc()    │        ├─► calc_node ──┐
│   ├ if 要查词 → dict()    │        └─► dict_node ──┤
│   └ 结果回填，继续循环     │                        ▼
└ 结束条件自己判断           │                     merge_node → END
流程藏在循环和 if 里         │        State={expr, calc_out, word, def_out, answer}
```

主干代码（各 ≤8 行，并排两栏）：

```python
# 写法A：SDK 手写（节选）            # 写法B：LangGraph（节选）
while True:                          g = StateGraph(S)
    msg = call_llm(msgs, tools)      g.add_node("calc", calc)
    if not msg.tool_calls: break     g.add_node("dict", lookup)
    msgs += run_tools(msg)           g.add_node("merge", merge)
print(msg.content)                   g.compile().invoke({"expr": "23*47"})
```

（演讲备注：A 的每一行你都能改，B 的每个节点你都能换——A 赢在小任务，B 赢在任务会长大。）

### P16｜9-2 开发 Agent 的通用步骤（带走的 checklist）

```
① 定义任务与边界      输入/输出是什么，什么坚决不做
② 列出所需工具        每个工具一句话：名字、参数、返回
③ 选流程范式          能预先分解 → Plan-and-Execute；探索型 → ReAct
④ 选实现层级          按第 8 章决策树：API / SDK / 框架
⑤ 实现+打印中间步骤    每轮「调了什么、参数、结果」必须可见
⑥ 加安全护栏          工具白名单、参数校验、轮次/成本上限
⑦ 观测与迭代          记录轨迹，按失败案例反哺提示词与工具
```

**一句话**：先跑通，再护栏，最后才谈优化——90% 的问题出在工具描述和任务边界，不在框架。

---

## 第 10 章　总结（1 页）

### P17｜演进主线 + 选型口诀

**演进主线**：

```
手拼 HTTP ──► SDK ──► 手写循环 ──► 框架执行器 ──► 图编排
  原理全见      通信省事    流程我定      循环现成        流程即资产
 └──────── 控制力 ────────►│◄──────── 省力 ────────┘
```

**选型口诀**：

> **简单用 API，多步用图，要给人用选 Dify；**
> **RAG 找 LlamaIndex，微软栈用 SK，前端选 Vercel。**

带走的三句话：
1. 所有框架底层都是同一个 POST——别怕，你已经在第 2 章见过它了。
2. 选型先选「组」再选「个」，按任务维度走决策树，不按热度。
3. 抽象降级不可逆：享受省力的同时，留出「能看中间步骤」的调试口。

---

## P18｜附录：三个可运行脚本（同一能力，三层写法）

| 脚本 | 对应章节 | 演示什么 | 依赖 |
|---|---|---|---|
| direct_api_demo.py | 第 2 章 | 只用标准 HTTP 库调 Chat Completions，打印原始返回 | requests |
| sdk_react_demo.py | 第 4 章 | SDK 手写 ReAct 循环 + 计算器工具，逐轮打印中间过程 | openai |
| langgraph_plan_demo.py | 第 7 章 | LangGraph 3~4 节点 Plan-and-Execute 图，打印节点流转 | langgraph |

三个脚本共用同一份接口配置（脚本顶部 CONFIG 区：`BASE_URL / API_KEY / MODEL`，兼容任何 Chat Completions 接口——云端 Key 或本地服务均可）。

### 附录脚本结构说明（确认大纲后完整交付）

**脚本 1：direct_api_demo.py（约 40 行）**
```
CONFIG 区（BASE_URL/API_KEY/MODEL）→ 构造 messages → requests.post
→ 打印原始 JSON → 解析 choices[0].message.content → 输出答案
```
要点：只用 requests；展示「构造 JSON → POST → 解析 choices」三步；打印原始返回让读者看清 API 真面目。

**脚本 2：sdk_react_demo.py（约 70 行）**
```
CONFIG 区 → 定义 calc(expr) 工具 + tools JSON Schema → messages 初始化
→ while 循环：调模型 → 打印[第n轮] → 有 tool_calls 则执行并回填（打印工具名/参数/结果）
→ 无 tool_calls 则输出最终回答结束
```
要点：每轮打印「模型要调哪个工具 → 参数 → 执行结果 → 回填」，对应 P7 的循环图。

**脚本 3：langgraph_plan_demo.py（约 80 行）**
```
CONFIG 区 → 定义 State(task/plan/results/answer) → 三个节点函数：
plan_node（LLM 拆步骤）→ act_node（逐步执行，可用 calc 工具）→ sum_node（汇总）
→ StateGraph 加边编译 → invoke 时每个节点打印 [NODE] 进入/输出
```
要点：打印节点流转顺序 plan→act→sum 与最终答案；说明换 checkpointer 即可获得断点恢复。

---

## P19｜结束页

- Q&A
- 一页资源：官方文档入口（OpenAI / LangGraph / Dify）+ 附录脚本获取方式
- 下篇预告（可选）：「让 Agent 可靠：护栏、评测与观测」

---

# 设计规范备忘（生成正式 PPT 时执行）

- 每章四块固定版式：左上「你可能的疑惑」→ 标题下「关键差异」1~2 句 → 中部 ASCII 架构图（等宽字体渲染）→ 右下角主干代码块（≤8 行）
- 对比类（P9/P10、P12~P15）优先表格或并排双框
- 代码块全部 ≤8 行，等宽字体，语法高亮 Python
- 不贴框架源码、不比 star/版本/性能、不展开 LangGraph 引擎内部
- 总页数 19，落在 18~22 区间
