# -*- coding: utf-8 -*-
"""
skill 配套脚本: 报销记录分类汇总
输入: 记录文件路径(可选; 无参数时使用内置示例数据)
      文本格式每行一条: 日期,项目,金额   如 2026-07-01,住宿,480.00
输出: 分类汇总打印 + 生成 报销单.csv(当前目录)
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

# 内置示例数据(无命令行参数时使用)
SAMPLE = """2026-07-01,住宿,480.00
2026-07-02,住宿,480.00
2026-07-02,餐饮,96.50
2026-07-03,交通,220.00
2026-07-03,餐饮,88.00"""


def read_records(path=None):
    if path:
        return Path(path).read_text(encoding="utf-8").strip().splitlines()
    return SAMPLE.strip().splitlines()


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    lines = read_records(path)

    rows, totals = [], defaultdict(float)
    for ln in lines:
        date, item, amount = [x.strip() for x in ln.split(",")]
        amt = round(float(amount), 2)
        rows.append((date, item, amt))
        totals[item] += amt

    out = Path("报销单.csv")
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["日期", "项目", "金额"])
        w.writerows(rows)
        w.writerow([])
        for item, t in sorted(totals.items()):
            w.writerow(["小计", item, f"{t:.2f}"])
        w.writerow(["总计", "", f"{sum(totals.values()):.2f}"])

    print("分类汇总:")
    for item, t in sorted(totals.items()):
        print(f"  {item}: {t:.2f} 元")
    print(f"总计: {sum(totals.values()):.2f} 元")
    print(f"已生成: {out.resolve()}")


if __name__ == "__main__":
    main()
