#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 ch1.html 抽出外壳（CSS + 播放器），生成一个空的新章节文件，保证外壳逐字一致。
用法：python3 newchapter.py ch2.html "第二章 · 从图灵到 Transformer"
"""
import re, sys

src = open("ch1.html", encoding="utf-8").read()
head, rest = src.split('<main id="slides">', 1)
_, tail = rest.split('<!--SLIDES-END-->', 1)

out, title = sys.argv[1], sys.argv[2]
head = re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, head, count=1)
open(out, "w", encoding="utf-8").write(
    head + '<main id="slides">\n\n<!--SLIDES-END-->' + tail)
print("written:", out)
