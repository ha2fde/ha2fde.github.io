# 仓库规矩

这是 `ha2fde.github.io`（GitHub Pages 个人站）。**任何 agent（Claude Code / opencode / WorkBuddy / 其他）动这个仓库前先读完这页。**
`CLAUDE.md` 只是一行指针，规矩只有这一份，别在别处再抄一遍。

站点有两个区，界线要干净：

- **对外区** —— 成品，首页链接，搜索引擎收录
- **归档区 `lab/`** —— 中间过程、半成品、旧版本，首页不链接，`noindex` + `robots.txt` 挡爬虫

## 东西往哪放

| 东西 | 去处 |
|---|---|
| 单个 HTML 文章，对外 | `posts/<名字>.html` |
| 多个文件的项目，对外 | `posts/<项目名>/`，入口必须叫 `index.html` |
| 中间过程 / 半成品 / 旧版本 | `lab/<项目名>/` |

根目录只应有：`index.html`、`README.md`、`AGENTS.md`、`CLAUDE.md`、`robots.txt`、`.nojekyll`、`.gitignore`、`posts/`、`lab/`、`tools/`、`.github/`。**别往根目录扔散文件。**

## 归档怎么推

```bash
python3 tools/lab_push.py <目录> --desc "一句话说明"     # Mac / Linux
python  tools\lab_push.py <目录> --desc "一句话说明"     # Windows
```

纯标准库，零安装。脚本会：忽略 `.workbuddy/`、`.git/`、`node_modules/` 和大二进制 → 打印文件清单等你回车 → 写 `lab/_meta.json` → `git pull --rebase` → commit → push。

`--name` 可以改归档名（默认取源目录名）。同名再推是增量覆盖，描述回车即保留旧的。

推完约一分钟，GitHub Actions 会自动重建 `lab/index.html`，去 <https://ha2fde.github.io/lab/> 看。

## 换一台机器

```bash
git clone --depth 1 https://github.com/ha2fde/ha2fde.github.io.git
```

配好 git 认证（`gh auth login`，或 PAT 走 HTTPS）—— 这步躲不掉。脚本已经在 `tools/` 里，Python 3 之外不需要装任何东西。

**注意**：这个仓库的历史被重写过（为了清掉 41 MB 的 PDF/PPTX）。老 clone 的机器 `git pull` 会失败，**重新 clone**，别试图 merge。

## 硬禁止

1. **不许手改 `lab/index.html`** —— GitHub Actions 生成，你改了下次 push 就被覆盖。要改样式改 `tools/gen_lab_index.py`。
2. **不许提交 PDF / PPTX / zip / 视频 / 模型权重** —— 这个仓库曾因此胀到 73 MB，清一次要重写历史。`.gitignore` 已经挡了，别用 `git add -f` 绕过去。派生产物就地重新生成，别进仓库。
3. **不许在 `index.html` 或任何对外页面链接 `/lab/`** —— 归档区靠"不链接 + noindex"隐身，链一次就前功尽弃。
4. **新增对外作品要手动在 `index.html` 作品区加卡片** —— 首页是手写的，没有生成器。
5. **不要在 `lab/` 里放密钥、token、私人聊天记录** —— 见下。

## 关于"不对外"的实话

仓库是 **public**。GitHub 个人站做不了访问控制（Enterprise 才有）。所以"不对外"= **首页不链接 + `noindex` + `robots.txt` 挡守规矩的爬虫**，不等于别人打不开。知道 URL 的人、或者翻 GitHub 仓库的人，照样看得到 `lab/` 里的一切。

**结论：`lab/` 是"不显眼"，不是"私密"。不能给人看的东西根本不要放进这个仓库。**

## 文件地图

```
index.html                 首页（手写：作品区 + 文章列表 + tab 过滤）
posts/                     对外区
lab/                       归档区
  index.html               ← Actions 生成，勿手改
  _meta.json               每个归档一句话说明
tools/lab_push.py          归档推送
tools/gen_lab_index.py     索引生成（本地与 CI 共用）
.github/workflows/lab-index.yml
```
