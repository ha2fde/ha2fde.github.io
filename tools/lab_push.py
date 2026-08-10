#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一个本地目录归档进 lab/ 并推上去。

纯标准库，Mac / Linux / Windows 通用：
    python3 tools/lab_push.py ~/WorkBuddy/2026-08-06-09-15-54 --desc "协议栈初稿"
    python  tools\\lab_push.py C:\\work\\something --name something --desc "..."

流程：复制 → 打印清单等你回车 → 写 _meta.json → pull --rebase → commit → push
lab/index.html 由 GitHub Actions 生成，本脚本不碰它。
"""

import argparse
import json
import os
import shutil
import subprocess
import sys

# Windows 控制台默认 GBK，打印 ✅ / ⚠️ / ❌ 会 UnicodeEncodeError。
# 崩的位置最坑：文件已复制、_meta.json 已写，但 git 一步没跑，看着像失败其实做了一半。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError, ValueError):
        pass  # 被重定向到不支持 reconfigure 的对象，忽略

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = os.path.join(ROOT, "lab")
META = os.path.join(LAB, "_meta.json")
MAX_FILE = 5 * 1024 * 1024  # 单文件上限，超了直接报错，不静默跳过

IGNORE_DIRS = {".git", ".workbuddy", "node_modules", "__pycache__", ".venv", "venv",
               ".idea", ".vscode", ".pytest_cache"}
IGNORE_EXT = {".pdf", ".pptx", ".ppt", ".zip", ".mp4", ".mov", ".bin", ".safetensors",
              ".gguf", ".pyc", ".DS_Store"}
IGNORE_NAMES = {".DS_Store", "Thumbs.db"}


def human(n):
    for unit in ("B", "K", "M", "G"):
        if n < 1024 or unit == "G":
            return f"{n:.0f}{unit}" if unit == "B" or n >= 10 else f"{n:.1f}{unit}"
        n /= 1024.0


def ignore_fn(directory, names):
    out = set()
    for n in names:
        p = os.path.join(directory, n)
        if os.path.isdir(p):
            if n in IGNORE_DIRS:
                out.add(n)
        else:
            if n in IGNORE_NAMES or os.path.splitext(n)[1].lower() in IGNORE_EXT:
                out.add(n)
    return out


def scan(src):
    """预扫描：返回 (保留文件列表, 被忽略文件列表, 超限文件列表)。"""
    keep, skipped, toobig = [], [], []
    for r, dirs, fs in os.walk(src):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in fs:
            p = os.path.join(r, f)
            rel = os.path.relpath(p, src).replace(os.sep, "/")
            if f in IGNORE_NAMES or os.path.splitext(f)[1].lower() in IGNORE_EXT:
                skipped.append(rel)
                continue
            try:
                sz = os.path.getsize(p)
            except OSError:
                continue
            if sz > MAX_FILE:
                toobig.append((rel, sz))
            keep.append((rel, sz))
    keep.sort()
    skipped.sort()
    return keep, skipped, toobig


def prune_empty(d):
    """删掉复制后变空的目录（源里的 .workbuddy/ 之类被 ignore 掉会留下空壳）。"""
    for r, dirs, fs in os.walk(d, topdown=False):
        if r == d:
            continue
        if not os.listdir(r):
            try:
                os.rmdir(r)
            except OSError:
                pass


def git(*a, check=True):
    return subprocess.run(["git", *a], cwd=ROOT, check=check)


def load_meta():
    if not os.path.exists(META):
        return {}
    try:
        return json.load(open(META, encoding="utf-8"))
    except ValueError as e:
        print(f"❌ lab/_meta.json 不是合法 JSON：{e}\n   先手动修好再跑。")
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description="归档一个目录到 lab/ 并推送")
    ap.add_argument("src", help="要归档的本地目录")
    ap.add_argument("--name", help="归档名（默认取源目录名）")
    ap.add_argument("--desc", help="一句话说明，写进 lab/_meta.json")
    ap.add_argument("--no-push", action="store_true", help="只复制和提交，不 push")
    args = ap.parse_args()

    src = os.path.abspath(os.path.expanduser(args.src.rstrip("/\\")))
    if not os.path.isdir(src):
        print(f"❌ 不是目录：{src}")
        return 1
    name = args.name or os.path.basename(src)
    dst = os.path.join(LAB, name)

    keep, skipped, toobig = scan(src)
    if not keep:
        print(f"❌ {src} 里没有可归档的文件（全被忽略规则挡掉了）")
        return 1
    if toobig:
        print(f"❌ 有文件超过 {human(MAX_FILE)}，仓库不收。要么先压缩/剥离，要么改 MAX_FILE：")
        for rel, sz in toobig:
            print(f"   {human(sz):>7}  {rel}")
        return 1

    total = sum(s for _, s in keep)
    print(f"\n源：{src}")
    print(f"目标：lab/{name}/")
    print(f"\n将归档 {len(keep)} 个文件，共 {human(total)}：")
    for rel, sz in keep:
        print(f"   {human(sz):>7}  {rel}")
    if skipped:
        print(f"\n已忽略 {len(skipped)} 个（工作记忆 / 大二进制 / 系统垃圾）：")
        for rel in skipped[:20]:
            print(f"           {rel}")
        if len(skipped) > 20:
            print(f"           …… 还有 {len(skipped) - 20} 个")
    if os.path.isdir(dst):
        print(f"\n⚠️  lab/{name}/ 已存在，同名文件会被覆盖（不删除已有的其他文件）")

    # 描述：同名再推时带出旧的，回车即保留
    meta = load_meta()
    old = (meta.get(name) or {}).get("desc", "")
    desc = args.desc
    if desc is None:
        prompt = f"\n一句话说明" + (f"（回车保留：{old}）" if old else "") + "："
        try:
            desc = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已取消")
            return 1
        if not desc:
            desc = old

    try:
        input("\n回车继续，Ctrl-C 取消 > ")
    except (EOFError, KeyboardInterrupt):
        print("\n已取消，什么都没动")
        return 1

    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=ignore_fn)
    prune_empty(dst)

    meta[name] = {"desc": desc, "src": args.src}
    with open(META, "w", encoding="utf-8", newline="") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    print(f"\n✅ 已复制到 lab/{name}/，说明已写入 _meta.json")

    # 必须先 commit 再 pull：带着未提交的改动 rebase 会被 git 直接拒绝
    git("add", "lab/")
    r = subprocess.run(["git", "commit", "-m", f"lab: {name}"], cwd=ROOT)
    if r.returncode != 0:
        print("（没有变化可提交）")
        return 0

    # Action 会把索引 commit 回 main，推之前得先 rebase 上去
    print("\n$ git pull --rebase")
    if subprocess.run(["git", "pull", "--rebase"], cwd=ROOT).returncode != 0:
        print("❌ pull --rebase 失败。改动已在本地提交，解决冲突后 git push 即可。")
        return 1

    if args.no_push:
        print("已提交，未推送（--no-push）")
        return 0
    if subprocess.run(["git", "push"], cwd=ROOT).returncode != 0:
        print("❌ push 失败。已在本地提交，网络/认证好了再 git push。")
        return 1

    print(f"\n🎉 完成。约一分钟后（Actions 跑完索引）：")
    print(f"   https://ha2fde.github.io/lab/{name}/")
    print(f"   https://ha2fde.github.io/lab/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
