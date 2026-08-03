# AGI Roadmap PPT · 版本管理

## 版本号规则

| 版本 | 含义 | 举例 |
|---|---|---|
| **v1, v2, v3…** | 大版本：整章重写、结构变动、新增章节等"伤筋动骨"的改动 | Chat 章从概念版 → 工程版 = v1 → v2 |
| **vX.1, vX.2…** | 小版本：在大版本基础上的微调（措辞、单页内容、配色、个别版式） | 改某页措辞、换强调色 = v2 → v2.1 |

## 目录结构

```
aippt/
├─ agi-roadmap.html            ← 主工作文件，永远是最新版
├─ VERSIONS.md                 ← 本文件，版本日志
└─ versions/                   ← 历史版本快照（每个都能独立打开演示）
   ├─ agi-roadmap-v1.html
   └─ agi-roadmap-v2.html
```

## 版本记录

### v2 （当前最新 = 主文件）
- **页数**：31 页
- **改动**：Chat 章由"概念版"重写为"工程实现版"（7 页 → 11 页）
  - 新增：三层架构、Base vs Instruct、对话格式本质（messages ↔ `<|im_start|>` token 序列）、SFT loss masking、4GB+QLoRA 实战、API 层（SSE/OpenAI 兼容）
  - 保留概念：三阶段总览、Transformer+Scaling Law、RLHF/DPO、推理 CoT/RLVR
- **新增版式**：代码块（token 着色/loss 灰显）、三层架构图、左右对照、表格
- **日期**：2026-07-30/31

### v1
- **页数**：27 页
- **说明**：首个完整版，四部分纯概念叙事（序章·苦涩的教训 / Chat / Agent / 终章·体验的时代）。Chat 章为概念版（Transformer、预训练、SFT、RLHF、推理）
- **日期**：2026-07-30

## 发版流程（由 AI 执行）

1. 在主文件 `agi-roadmap.html` 上修改
2. 复制快照：`cp agi-roadmap.html versions/agi-roadmap-v<版本号>.html`
3. 在本文件追加版本记录
4. 大改动升大版本号，微调升小版本号
