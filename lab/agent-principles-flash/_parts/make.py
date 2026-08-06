#!/usr/bin/env python3
import sys, pathlib

parts = pathlib.Path(__file__).resolve().parent
root = parts.parent

def build(ch: str, title: str):
    head = (parts / 'head.html').read_text(encoding='utf-8').replace('__TITLE__', title)
    slides = (parts / f'slides_ch{ch}.html').read_text(encoding='utf-8')
    foot = (parts / 'foot.html').read_text(encoding='utf-8')
    (root / f'ch{ch}.html').write_text(head + slides + foot, encoding='utf-8')
    print(f'wrote ch{ch}.html')

if __name__ == '__main__':
    # usage: make.py <ch> <title>
    build(sys.argv[1], sys.argv[2])
