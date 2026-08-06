# Agent 的协议层 · HTML PPT

第三段旅程：**Tools · MCP · CLI · Skills · A2A**，以及把它们统一起来的 **ACI（Agent–Computer Interface）**。

前两段（AI → Transformer、chat → agent）不在本讲范围内。

## 两个文件，两种用法

| 文件 | 页数 | 定位 |
|---|---|---|
| `deck-deep.html` | **55 页** | 自己啃透用。含完整时序大图、真实报文、正反例、规范演进史、七条 ACI 设计原则、安全清单、生态数据与判断 |
| `deck-lite.html` | **26 页** | 讲给别人听用。每页只留**一个结论 + 一张图**，删掉演进史、反例清单、展开材料 |

精简版**不是**深讲版的隐藏页版本，是独立写的一篇。两者可以分开看。

直接双击打开即可，或：

```bash
open deck-deep.html
open deck-lite.html
```

**零构建、零 CDN、零外部依赖，断网可用。** 已核实两个文件中没有任何 `http(s)` 资源引用。

## 快捷键

| 键 | 作用 |
|---|---|
| `→` / `PageDown` / `Space` / `J` | 下一页 |
| `←` / `PageUp` / `K` | 上一页 |
| `Home` / `End` | 首页 / 末页 |
| `O` | 概览网格（再按 `O` 或 `Esc` 退出，点缩略图跳转） |
| `F` | 全屏 |

鼠标：点左侧 28% 区域上一页，其余区域下一页。触屏：左右滑动（阈值 50px）。

地址栏 `#30` 直达第 30 页，翻页时 hash 会同步。

## 深讲版结构

| 幕 | 页 | 内容 |
|---|---|---|
| 0 · 开场 | 1–3 | 三段旅程地图 · 结论先行：只有一个主角叫 ACI |
| 1 · Tools | 4–11 | tool 真实定义 · 一次完整往返时序 · **模型从不执行** · `tool_choice` 四档 · description 就是接口文档 · 工具变多以后 |
| 2 · MCP | 12–24 | N×M 问题 · **四实体一张图** · 三个误解 · 两种传输 · **完整时序大图** · 真实报文（发现 / 调用）· 三原语按「谁决定」分层 · 反向三原语 · **拍平成 tools** · 规范演进线 · **2026-07-28 无状态转向** |
| 3 · CLI | 25–29 | 最老最暴力的 ACI · 无 schema 工具 · 三条优势 · 四项代价 · **升级成专用工具的分界线** |
| 4 · 共通本质 | 30–34 | 三者对齐大表 · 同一个三段式 · **ACI 是什么** · 设计七条 · **选型决策树** |
| 5 · Skills | 35–43 | 管的是「该怎么做」· SKILL.md 真实长相 · **渐进式披露三层** · API 形态 · 编写要点 · 分发渠道 · 应用场景 · 安全 · 未来判断 |
| 6 · A2A | 44–52 | **换了一个维度** · 四个角色 · **AgentCard 真实 JSON** · 发现→委派→协商→交付时序 · **Task 八态状态机** · 长任务两种回传 · 治理与版本线 · 生态现实与「为什么你还没用上」· A2A vs MCP |
| 7 · 收尾 | 53–55 | 五者同一坐标系总图 · 五条能带走的判断 · 结束页 |

## 事实基线（核对日期：2026-08-06）

幻灯片里所有会随时间变化的数字都标注了口径与日期。核心事实：

**MCP**
- 修订线：`2024-11-05` → `2025-03-26` → `2025-06-18` → `2025-11-25` → **`2026-07-28`（现行）**
- 2026-07-28 的破坏性变更：无状态核心；取消 `initialize` 握手与 `notifications/initialized`；取消会话与 `Mcp-Session-Id`；版本与能力改挂 `_meta`（`io.modelcontextprotocol/protocolVersion`、`io.modelcontextprotocol/clientCapabilities`）；服务端自签句柄作为普通工具参数；基于 header 的路由；MRTR；扩展框架（Tasks、MCP Apps）；授权加固与废弃策略
- 传输：stdio 子进程 / Streamable HTTP（+ SSE、OAuth）
- 原语按控制权分层：Tools=模型决定 · Resources=应用决定 · Prompts=用户决定；反向：Sampling / Roots / Elicitation
- 规范原文：<https://modelcontextprotocol.io/specification>

**Skills**
- 2025-10 发布；2025-12-18 以开放标准发布于 <https://agentskills.io>
- 市场数：2025-12 的 1 个 → 2026 Q2 的 8 个主要市场（含 Vercel `skills.sh`、SkillsMP 等）
- 数量级：数千 → 2026-01 数万 → 2026-03 中旬 40 万+；索引量报道到百万级
- 兼容产品数各来源口径差异较大（十几到四十余款），幻灯片中按区间表述
- API 形态：`container.skills` + `code_execution_20260521`，beta header `code-execution-2025-08-25` / `skills-2025-10-02`；`GET /v1/skills`
- SKILL.md frontmatter：`name` / `description` / `license` / `allowed-tools`

**A2A**
- 2025-04 由 Google 发布 → **2025-06-23 捐给 Linux Foundation** → 2025-08 IBM ACP 并入 → 2026 年初 **v1.0（Signed Agent Cards）** → 2026-05 **v1.0.1（扩展机制）**
- AgentCard 发布于 `/.well-known/agent-card.json`
- 传输：JSON-RPC 2.0（另有 gRPC、HTTP+JSON 绑定）
- 方法：`message/send` · `message/stream` · `tasks/get` · `tasks/cancel` · `tasks/resubscribe` · `tasks/pushNotificationConfig/set`
- Task 八态：`submitted` `working` `input_required` `auth_required` `completed` `failed` `canceled` `rejected`
- 生态：150+ 组织、22,000+ GitHub stars、5 种语言生产级 SDK、配套 AP2（Agent Payments Protocol）、Copilot Studio / Azure AI Foundry / Bedrock AgentCore 已 GA
- 规范原文：<https://a2a-protocol.org>

### 关于数字的一句提醒

生态类数据（市场数、skill 总量、组织数、star 数）变化很快，且不少来源带有厂商口径偏差。
**引用前请按上面的官方链接重新核实**——幻灯片里对这一点做了显式标注。

## 验收记录（2026-08-06）

用 Chrome headless 对每一页逐页测量 `.body` 的 `scrollHeight` vs `clientHeight`（纵向溢出）与所有非 SVG 子元素的 `scrollWidth` vs `clientWidth`（横向溢出）：

```
deck-deep.html  TOTAL=55  ALL-CLEAR
deck-lite.html  TOTAL=26  ALL-CLEAR
```

在 1400×900 与 980×660 两种窗口下结果一致（画布固定 1280×720 + scale-to-fit，布局与视口无关）。
hash 直达（`#30`、`#55`、`#22`）与 HUD 幕标签、进度条均已验证。

页面自带溢出检测：切页时如有内容超出画布，会在 Console 打 `[溢出]` 警告并给该页加红色 outline。**正常情况下应当全程无警告。**

## 设计约定

- 所有图一律 **inline SVG 或 HTML/CSS 组件**，不用 ASCII 字符画（字符网格在不同字体下必然错位，换字体救不了）
- 固定 1280×720 画布，`transform: scale(min(vw/1280, vh/720) × 0.955))` 适配窗口
- 语义色：<span>蓝</span> = 数据流 / 客户端 · 绿 = 产出 / 正确 · 橙 = 工程要点 · 紫 = 模型 / 协议 · 红 = 坑 / 失效
