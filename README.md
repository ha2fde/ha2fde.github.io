# Ha2fde's Site

My personal website hosted on GitHub Pages.

Visit: https://ha2fde.github.io

---

## AI Agent 系列培训 · 整合版

七讲一条主线：**用起来 → 懂原理 → 会开发 → 能落地 → 看远方**。一份资料，三种形态：单文件书、分讲幻灯片、可运行脚本。资料集中在 **[`ai-agent-training/`](ai-agent-training/)** 子目录，与本站其余内容相互独立。

👉 **在线阅读（推荐）**：[ai-agent-training/book.html](ai-agent-training/book.html) — 七讲整合进一个 HTML 文件（约 0.49 MB，离线可读，像一本书）。
👉 **资料总览页**：[ai-agent-training/index.html](ai-agent-training/index.html)（含脚本 / HTML / PDF / PPTX 全部入口）。

### 目录结构（ai-agent-training/）

| 内容 | 形态 | 入口 |
|---|---|---|
| **单文件书** | HTML（推荐） | [`book.html`](ai-agent-training/book.html) |
| **七讲幻灯片** | HTML | [`slides/`](ai-agent-training/slides/) — 01~07 共 7 讲 |
| **配套脚本** | Python ×17 + 1 Skill | [`scripts/index.html`](ai-agent-training/scripts/index.html)（索引页，带说明与复制） |
| **PDF 导出** | 16:9 PDF | [`exports/`](ai-agent-training/exports/) — `00-全书合订本.pdf`（158 页）+ 七讲分讲 |
| **PPTX** | 放映版 + 原生可编辑 | [`pptx/`](ai-agent-training/pptx/) |
| **构建/导出脚本** | Python | [`build_book.py`](ai-agent-training/build_book.py) · [`export_pdf.py`](ai-agent-training/export_pdf.py) · [`pdf_to_pptx.py`](ai-agent-training/pdf_to_pptx.py) |
| **版本记录** | Markdown | [`VERSIONS.md`](ai-agent-training/VERSIONS.md)（当前 v2.1） |

### 七讲一览

1. **破冰指南**（全员）— [HTML](ai-agent-training/slides/01-破冰指南.html) · [PDF](ai-agent-training/exports/01-破冰指南.pdf) · [PPTX](ai-agent-training/pptx/01-破冰指南（放映版）.pptx)
2. **从计算机到 GPT**（懂技术）— [HTML](ai-agent-training/slides/02-从计算机到GPT.html) · [PDF](ai-agent-training/exports/02-从计算机到GPT.pdf) · [PPTX](ai-agent-training/pptx/02-从计算机到GPT（放映版）.pptx)
3. **ChatGPT 是怎么工作的**（懂技术）— [HTML](ai-agent-training/slides/03-ChatGPT是怎么工作的.html) · [PDF](ai-agent-training/exports/03-ChatGPT是怎么工作的.pdf) · [PPTX](ai-agent-training/pptx/03-ChatGPT是怎么工作的（放映版）.pptx)
4. **开发 Agent**（开发者）— [HTML](ai-agent-training/slides/04-开发Agent.html) · [PDF](ai-agent-training/exports/04-开发Agent.pdf) · [PPTX](ai-agent-training/pptx/04-开发Agent（放映版）.pptx) / [原生可编辑](ai-agent-training/pptx/开发Agent-从API到框架编排.pptx)
5. **Agent 工程化全景**（技术+管理）— [HTML](ai-agent-training/slides/05-Agent工程化全景.html) · [PDF](ai-agent-training/exports/05-Agent工程化全景.pdf) · [PPTX](ai-agent-training/pptx/05-Agent工程化全景（放映版）.pptx)
6. **通往 AGI 之路**（收束篇）— [HTML](ai-agent-training/slides/06-通往AGI之路.html) · [PDF](ai-agent-training/exports/06-通往AGI之路.pdf) · [PPTX](ai-agent-training/pptx/06-通往AGI之路（放映版）.pptx)
7. **资料索引**（全员）— [HTML](ai-agent-training/slides/07-资料索引.html) · [PDF](ai-agent-training/exports/07-资料索引.pdf) · [PPTX](ai-agent-training/pptx/07-资料索引（放映版）.pptx)

### 本地重新生成

```bash
pip install pymupdf python-pptx
python build_book.py        # slides/ 七讲 → book.html 单文件书
python export_pdf.py        # 七讲 HTML → exports/*.pdf
python pdf_to_pptx.py       # exports/*.pdf → pptx/*.pptx
```

> 资料与本站其余页面相互独立；`ai-agent-training/` 内的相对链接在 GitHub Pages 与本地 `file://` 下均可正常打开。
