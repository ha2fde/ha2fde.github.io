# -*- coding: utf-8 -*-
"""批量把 integrated/slides 下七讲 HTML 打印为 16:9 PDF，输出到 integrated/exports/"""
import os, re, subprocess, urllib.parse, sys

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ROOT = r"C:\Users\think\WorkBuddy\aippt8"
SLIDES = os.path.join(ROOT, "integrated", "slides")
OUT = os.path.join(ROOT, "integrated", "exports")
BASE = "http://127.0.0.1:8931/integrated/slides/"

os.makedirs(OUT, exist_ok=True)

files = sorted(f for f in os.listdir(SLIDES) if f.endswith(".html"))
for fn in files:
    url = BASE + urllib.parse.quote(fn)
    pdf = os.path.join(OUT, fn[:-5] + ".pdf")
    cmd = [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
           "--no-pdf-header-footer", "--virtual-time-budget=4000",
           "--print-to-pdf=" + pdf, url]
    subprocess.run(cmd, capture_output=True, timeout=180)
    if os.path.exists(pdf):
        data = open(pdf, "rb").read()
        pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
        mb = re.findall(rb"MediaBox\s*\[([^\]]+)\]", data)
        size = mb[0].decode().strip() if mb else "?"
        print("OK  %-34s %2d 页  MediaBox[%s]  %.1f KB" % (fn[:-5], pages, size, len(data) / 1024))
    else:
        print("FAIL", fn)
