#!/usr/bin/env python3
"""统计各省份采集结果质量等级"""
import json
import sys
from pathlib import Path

data = json.load(open(Path(__file__).parent.parent / "output" / "all_provinces.json", encoding="utf-8"))

print(f"{'省份':<8} {'条件':<5} {'材料':<5} {'时限':<5} {'电话':<5} {'告警':<5} {'评级'}")
print("-" * 60)
for p in data:
    cond = len(p.get("apply_conditions") or [])
    mat = len(p.get("required_materials") or [])
    rd = bool(p.get("review_deadline"))
    ht = bool(p.get("hotline"))
    warns = len(p.get("parse_warnings") or [])
    err = bool(p.get("error"))

    # 评级
    if err or (cond == 0 and mat == 0):
        grade = "🔴 red"
    elif cond >= 3 and mat >= 3 and rd and ht:
        grade = "🟢 green"
    elif cond >= 3 and (mat >= 1 or rd):
        grade = "🟡 yellow"
    else:
        grade = "🟠 orange"

    rd_s = "Y" if rd else "."
    ht_s = "Y" if ht else "."
    print(f"{p['province']:<8} {cond:<5} {mat:<5} {rd_s:<5} {ht_s:<5} {warns:<5} {grade}")

# 总览
total = len(data)
green = yellow = orange = red = 0
for p in data:
    cond = len(p.get("apply_conditions") or [])
    mat = len(p.get("required_materials") or [])
    rd = bool(p.get("review_deadline"))
    ht = bool(p.get("hotline"))
    err = bool(p.get("error"))
    if err or (cond == 0 and mat == 0):
        red += 1
    elif cond >= 3 and mat >= 3 and rd and ht:
        green += 1
    elif cond >= 3 and (mat >= 1 or rd):
        yellow += 1
    else:
        orange += 1
print()
print(f"共 {total} 省：🟢{green}  🟡{yellow}  🟠{orange}  🔴{red}")
