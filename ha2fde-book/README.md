# AI Agent 系列培训 · 整合版

七讲一条主线：**用起来 → 懂原理 → 会开发 → 能落地 → 看远方**。一份资料，三种形态：单文件书、分讲幻灯片、可运行脚本。

👉 **在线阅读（推荐）**：[`book.html`](book.html) — 七讲整合进一个 HTML 文件（约 0.49 MB，离线可读，像一本书）。
👉 **本目录总览页**：[`index.html`](index.html)（脚本 / HTML / PDF / PPTX 全部入口）。

## 目录

| 内容 | 入口 |
|---|---|
| 单文件书（HTML） | [`book.html`](book.html) |
| 七讲幻灯片（HTML） | [`slides/`](slides/) — 01~07 |
| 配套脚本（Python ×17 + 1 Skill） | [`scripts/index.html`](scripts/index.html)（带说明的索引页） |
| PDF 导出（16:9） | [`exports/`](exports/) — `00-全书合订本.pdf`（158 页）+ 七讲分讲 |
| PPTX（放映版 + 原生可编辑） | [`pptx/`](pptx/) |
| 构建 / 导出脚本 | [`build_book.py`](build_book.py) · [`export_pdf.py`](export_pdf.py) · [`pdf_to_pptx.py`](pdf_to_pptx.py) |
| 版本记录 | [`VERSIONS.md`](VERSIONS.md)（当前 v2.1） |
| 下载中心 | [`downloads.html`](downloads.html) |

## 本地重新生成

```bash
pip install pymupdf python-pptx
python build_book.py        # slides/ 七讲 → book.html
python export_pdf.py        # 七讲 HTML → exports/*.pdf
python pdf_to_pptx.py       # exports/*.pdf → pptx/*.pptx
```

> 本目录相对链接在 GitHub Pages 与本地 `file://` 下均可正常打开。
