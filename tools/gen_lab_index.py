#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 lab/index.html —— 归档区索引。

纯标准库，Mac / Linux / Windows 通用。本地和 GitHub Actions 跑的是同一份。

做两件事：
  1. 给 lab/ 下每个 .html 幂等注入 <meta name="robots" content="noindex,nofollow">
  2. 扫描 lab/*/ 生成索引页（按最后改动倒序，带前端搜索框）

用法：python3 tools/gen_lab_index.py
"""

import html
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = os.path.join(ROOT, "lab")
NOINDEX = '<meta name="robots" content="noindex,nofollow">'

# 这些不算「内容文件」，不进文件列表也不计数
SKIP_NAMES = {".DS_Store", "Thumbs.db"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".workbuddy"}


def human(n):
    for unit in ("B", "K", "M", "G"):
        if n < 1024 or unit == "G":
            return f"{n:.0f}{unit}" if unit == "B" or n >= 10 else f"{n:.1f}{unit}"
        n /= 1024.0


def walk_files(d):
    """返回 (相对路径, 字节数) 列表，路径用 / 分隔（Windows 也是）。"""
    out = []
    for r, dirs, fs in os.walk(d):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in fs:
            if f in SKIP_NAMES:
                continue
            p = os.path.join(r, f)
            rel = os.path.relpath(p, d).replace(os.sep, "/")
            try:
                out.append((rel, os.path.getsize(p)))
            except OSError:
                pass
    out.sort()
    return out


def git_date(relpath):
    """该路径最后一次提交的日期（YYYY-MM-DD）。未提交/无 git 时回退到文件 mtime。"""
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", relpath],
            cwd=ROOT, capture_output=True, text=True, timeout=20,
        )
        d = r.stdout.strip()
        if d:
            return d
    except Exception:
        pass
    import datetime
    newest = 0
    for rr, ds, fs in os.walk(os.path.join(ROOT, relpath)):
        ds[:] = [x for x in ds if x not in SKIP_DIRS]
        for f in fs:
            try:
                newest = max(newest, os.path.getmtime(os.path.join(rr, f)))
            except OSError:
                pass
    if not newest:
        return "—"
    return datetime.date.fromtimestamp(newest).isoformat()


def inject_noindex():
    """给 lab/ 下所有 .html 加 noindex。已有则跳过。返回改动数。"""
    n = 0
    for r, dirs, fs in os.walk(LAB):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in fs:
            if not f.lower().endswith((".html", ".htm")):
                continue
            p = os.path.join(r, f)
            if os.path.abspath(p) == os.path.join(LAB, "index.html"):
                continue  # 本脚本自己生成的，模板里已带
            try:
                s = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            if 'name="robots"' in s:
                continue
            low = s.lower()
            i = low.find("<head>")
            if i >= 0:
                s = s[:i + 6] + "\n" + NOINDEX + s[i + 6:]
            else:
                i = low.find("<html")
                j = s.find(">", i) + 1 if i >= 0 else 0
                s = s[:j] + "\n<head>" + NOINDEX + "</head>" + s[j:]
            open(p, "w", encoding="utf-8", newline="").write(s)
            n += 1
    return n


def entry_of(name, files):
    """入口文件：index.html 优先，其次唯一的 .html，都没有则 None。"""
    names = [f for f, _ in files]
    if "index.html" in names:
        return "index.html"
    htmls = [f for f in names if f.lower().endswith((".html", ".htm"))]
    if len(htmls) == 1:
        return htmls[0]
    # 顶层唯一的 html（如 workbuddy/<时间戳>/x.html 这种嵌套就不算）
    top = [f for f in htmls if "/" not in f]
    if len(top) == 1:
        return top[0]
    return None


def collect():
    meta = {}
    mp = os.path.join(LAB, "_meta.json")
    if os.path.exists(mp):
        try:
            meta = json.load(open(mp, encoding="utf-8"))
        except ValueError as e:
            print(f"⚠️  _meta.json 解析失败，描述将为空：{e}", file=sys.stderr)

    items = []
    for name in sorted(os.listdir(LAB)):
        d = os.path.join(LAB, name)
        if not os.path.isdir(d) or name in SKIP_DIRS:
            continue
        files = walk_files(d)
        if not files:
            continue
        items.append({
            "name": name,
            "desc": (meta.get(name) or {}).get("desc", ""),
            "src": (meta.get(name) or {}).get("src", ""),
            "files": files,
            "count": len(files),
            "size": human(sum(s for _, s in files)),
            "date": git_date(f"lab/{name}"),
            "entry": entry_of(name, files),
        })
    items.sort(key=lambda x: (x["date"], x["name"]), reverse=True)
    return items


CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans SC', sans-serif;
    background: #f8f9fa; color: #333; line-height: 1.7;
}
.container { max-width: 800px; margin: 0 auto; padding: 2rem 1.5rem; }
header { padding: 2.5rem 0 1.5rem; border-bottom: 1px solid #eee; margin-bottom: 1.2rem; }
header h1 { font-size: 2rem; color: #1a1a2e; }
header p { color: #666; margin-top: 0.3rem; }
.badge {
    display: inline-block; font-size: 0.75rem; font-weight: 600; padding: 0.15rem 0.5rem;
    border-radius: 4px; background: #fff3e0; color: #e67e22; margin-left: 0.5rem;
    vertical-align: middle;
}
#q {
    width: 100%; padding: 0.65rem 0.9rem; font-size: 1rem; border: 1px solid #ddd;
    border-radius: 8px; background: #fff; margin-bottom: 0.5rem; font-family: inherit;
}
#q:focus { outline: none; border-color: #3498db; }
.count { font-size: 0.85rem; color: #999; margin-bottom: 1rem; }

.post { padding: 1.4rem 0; border-bottom: 1px solid #eee; }
.post:last-child { border-bottom: none; }
.post-title { font-size: 1.25rem; font-weight: 600; }
.post-title a { color: #1a1a2e; text-decoration: none; }
.post-title a:hover { color: #3498db; }
.post-title span.noentry { color: #1a1a2e; }
.post-meta { font-size: 0.85rem; color: #999; margin-top: 0.3rem; }
.post-desc { font-size: 0.95rem; color: #555; margin-top: 0.5rem; }
.hidden { display: none !important; }

details { margin-top: 0.6rem; }
summary {
    font-size: 0.85rem; color: #3498db; cursor: pointer; user-select: none;
    list-style: none; display: inline-block;
}
summary::-webkit-details-marker { display: none; }
summary::before { content: '▸ '; }
details[open] summary::before { content: '▾ '; }
.files { margin-top: 0.5rem; font-size: 0.85rem; }
.files a { display: block; color: #555; text-decoration: none; padding: 0.15rem 0; word-break: break-all; }
.files a:hover { color: #3498db; text-decoration: underline; }
.files .sz { color: #bbb; font-size: 0.78rem; margin-left: 0.4rem; }

footer { text-align: center; padding: 2rem; color: #999; font-size: 0.85rem; }

@media (max-width: 600px) {
    .container { padding: 1.2rem 1rem; }
    header { padding: 1.5rem 0 1rem; }
    header h1 { font-size: 1.5rem; }
    .post-title { font-size: 1.1rem; }
}
"""

JS = """
(function () {
    var q = document.getElementById('q');
    var cards = Array.prototype.slice.call(document.querySelectorAll('.post'));
    var out = document.getElementById('count');
    function run() {
        var k = q.value.trim().toLowerCase();
        var n = 0;
        cards.forEach(function (c) {
            var hit = !k || c.dataset.search.indexOf(k) >= 0;
            c.classList.toggle('hidden', !hit);
            if (hit) n++;
        });
        out.textContent = k ? (n + ' / ' + cards.length + ' 项') : (cards.length + ' 项归档');
    }
    q.addEventListener('input', run);
    run();
})();
"""


def render(items):
    e = html.escape
    parts = []
    for it in items:
        title = e(it["name"])
        if it["entry"]:
            t = f'<a href="{e(it["name"])}/{e(it["entry"])}">{title}</a>'
        else:
            t = f'<span class="noentry">{title}</span>'

        flist = "\n".join(
            f'          <a href="{e(it["name"])}/{e(f)}">{e(f)}<span class="sz">{human(s)}</span></a>'
            for f, s in it["files"]
        )
        search = " ".join([it["name"], it["desc"], it["src"]] + [f for f, _ in it["files"]]).lower()
        desc = f'\n        <div class="post-desc">{e(it["desc"])}</div>' if it["desc"] else ""
        src = f' · 来源 {e(it["src"])}' if it["src"] else ""

        parts.append(f"""      <div class="post" data-search="{e(search)}">
        <div class="post-title">{t}</div>
        <div class="post-meta">{it["date"]} · {it["count"]} 个文件 · {it["size"]}{src}</div>{desc}
        <details>
          <summary>展开全部文件</summary>
          <div class="files">
{flist}
          </div>
        </details>
      </div>""")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
{NOINDEX}
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>归档 · Lab</title>
<style>{CSS}</style>
</head>
<body>
  <div class="container">
    <header>
      <h1>归档<span class="badge">不对外索引</span></h1>
      <p>中间过程、半成品、旧版本。首页不链接这里，搜索引擎不收录。</p>
    </header>

    <input id="q" type="search" placeholder="搜索归档名、说明、文件名…" autocomplete="off">
    <div class="count" id="count"></div>

{chr(10).join(parts)}

  </div>
  <footer>本页由 tools/gen_lab_index.py 生成，请勿手改</footer>
  <script>{JS}</script>
</body>
</html>
"""


def main():
    if not os.path.isdir(LAB):
        print("lab/ 不存在，跳过", file=sys.stderr)
        return 0
    n = inject_noindex()
    items = collect()
    open(os.path.join(LAB, "index.html"), "w", encoding="utf-8", newline="").write(render(items))
    print(f"✅ lab/index.html 已生成：{len(items)} 项归档，注入 noindex {n} 个文件")
    for it in items:
        print(f"   {it['date']}  {it['name']:<24} {it['count']:>3} 文件  {it['size']:>6}  "
              f"{'入口:' + it['entry'] if it['entry'] else '（无单一入口）'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
