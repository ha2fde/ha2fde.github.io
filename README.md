# ha2fde.github.io

个人站点，GitHub Pages 托管：<https://ha2fde.github.io>

分两个区：**对外区**放成品，首页链接、搜索引擎收录；**归档区 `lab/`** 放中间过程和旧版本，首页不链接、`noindex` + `robots.txt` 挡爬虫（仓库是 public，所以这是"不显眼"而非"私密"）。

## 东西往哪放

| 东西 | 去处 |
|---|---|
| 单个 HTML 文章，对外 | `posts/<名字>.html` |
| 多个文件的项目，对外 | `posts/<项目名>/`，入口必须叫 `index.html` |
| 中间过程 / 半成品 / 旧版本 | `lab/<项目名>/` |

## 归档一个目录

```bash
python3 tools/lab_push.py <目录> --desc "一句话说明"     # Windows: python tools\lab_push.py ...
```

纯标准库零安装。复制 → 确认清单 → 写说明 → push。`lab/index.html` 由 GitHub Actions 重建，**不要手改**。

## 完整规矩

见 **[AGENTS.md](AGENTS.md)** —— 三层规则、换机器、硬禁止（不提交大二进制、不链接 `/lab/`）。所有 agent 动这个仓库前都读那一份，这里只是摘要。
