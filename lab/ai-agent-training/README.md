# AI Agent 系列培训 · 整合版

七讲一条主线：**用起来 → 懂原理 → 会开发 → 能落地 → 看远方**。一份资料，三种形态：单文件书、分讲幻灯片、可运行脚本。

> **归档件。** 这是 2026-08 之前的旧版培训材料，已从对外区移入 `lab/`。最新的一版是 [`posts/agent-principles/`](../../posts/agent-principles/)。

👉 **在线阅读（推荐）**：[`book.html`](book.html) — 七讲整合进一个 HTML 文件（约 0.49 MB，离线可读，像一本书）。
👉 **本目录总览页**：[`index.html`](index.html)。

## 目录

| 内容 | 入口 |
|---|---|
| 单文件书（HTML） | [`book.html`](book.html) |
| 七讲幻灯片（HTML） | [`slides/`](slides/) — 01~07 |
| 配套脚本（Python ×17 + 1 Skill） | [`scripts/index.html`](scripts/index.html)（带说明的索引页） |
| 构建 / 导出脚本 | [`build_book.py`](build_book.py) · [`export_pdf.py`](export_pdf.py) · [`pdf_to_pptx.py`](pdf_to_pptx.py) |
| 下载中心（HTML 入口） | [`downloads.html`](downloads.html) |

## 七讲一览

1. **破冰指南**（全员）— [HTML](slides/01-破冰指南.html)
2. **从计算机到 GPT**（懂技术）— [HTML](slides/02-从计算机到GPT.html)
3. **ChatGPT 是怎么工作的**（懂技术）— [HTML](slides/03-ChatGPT是怎么工作的.html)
4. **开发 Agent**（开发者）— [HTML](slides/04-开发Agent.html)
5. **Agent 工程化全景**（技术+管理）— [HTML](slides/05-Agent工程化全景.html)
6. **通往 AGI 之路**（收束篇）— [HTML](slides/06-通往AGI之路.html)
7. **资料索引**（全员）— [HTML](slides/07-资料索引.html)

## PDF / PPTX 去哪了

**已从仓库剥离**（原本 41 MB：22 MB PDF + 19 MB PPTX，把仓库撑到了 73 MB）。它们是纯派生产物，需要时本地重新生成：

```bash
pip install pymupdf python-pptx
python build_book.py        # slides/ 七讲 → book.html
python export_pdf.py        # 七讲 HTML → exports/*.pdf
python pdf_to_pptx.py       # exports/*.pdf → pptx/*.pptx
```

也可以直接在幻灯片网页里按 `P` 或 Ctrl+P 导出 PDF：纸张选「横向」、边距「无」、勾选「背景图形」、缩放 100%，即得同样的 16:9 PDF。

> 本目录相对链接在 GitHub Pages 与本地 `file://` 下均可正常打开。
