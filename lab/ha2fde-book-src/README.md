# AI Agent 实战手册 · 构建源

`lab/ha2fde-book/`（站上发布过的成品版七章）就是这里生成出来的。归档件，留着是为了以后还能重新生成。

| 内容 | 入口 |
|---|---|
| 单文件书（生成结果，约 0.49 MB） | [`book.html`](book.html) |
| 生成器 | [`build_book.py`](build_book.py) |
| 配套脚本源 | `scripts/lecture2/` · `scripts/lecture3/` · `scripts/lecture4/` |

```bash
python build_book.py    # 各讲 HTML → book.html
```

分讲幻灯片、导出脚本和成品页在 [`../ai-agent-training/`](../ai-agent-training/)；PDF / PPTX 已从仓库剥离，需要时本地重新生成（见那边的 README）。
