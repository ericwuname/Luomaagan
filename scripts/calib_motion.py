#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
诊断脚本校准 —— 用「已知答案」验证 zoom 判据方向

起因：我对 S2 做了 Ken Burns 推镜（1.0→1.28，确定是推近），
     诊断脚本却报 zoom=-0.43（判为拉远）。

**如果判据反了，之前所有"运动方向不对"的结论都要倒过来看。**
所以必须先校准：造两个已知答案的视频，看诊断给出什么。
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


kb = load("kb", os.path.join(HERE, "ken_burns.py"))
dm = load("dm", os.path.join(HERE, "diag_motion.py"))

CAL = os.path.join(ROOT, "work", "ep01", "clips_kb", "_cal")
os.makedirs(CAL, exist_ok=True)

# 用一张有丰富细节的图（S7 全景）
SRC = os.path.join(ROOT, "work", "ep01", "S7_rooftop.png")

TESTS = [
    ("PUSH_1.00_to_1.60", 1.00, 1.60, "推近"),
    ("PULL_1.60_to_1.00", 1.60, 1.00, "拉远"),
    ("PUSH_1.00_to_1.20", 1.00, 1.20, "推近(轻微)"),
    ("PULL_1.20_to_1.00", 1.20, 1.00, "拉远(轻微)"),
    ("STATIC_1.00", 1.00, 1.00, "固定"),
]

print(f"{'测试':24s} {'真实':12s} {'诊断zoom':>10s}  判定")
print("-" * 78)
for name, s0, s1, truth in TESTS:
    dst = os.path.join(CAL, name + ".mp4")
    if not os.path.exists(dst):
        kb.ken_burns(SRC, dst, 3.0, s0, s1, (0.5, 0.5), 1.8)
    r = dm.analyze(dst)
    verdict = dm.describe(r)
    ok = ""
    if truth == "推近" or truth.startswith("推近"):
        ok = "✓" if r["zoom"] > 0.15 else "✗ 反了"
    elif truth == "拉远" or truth.startswith("拉远"):
        ok = "✓" if r["zoom"] < -0.15 else "✗ 反了"
    else:
        ok = "✓" if abs(r["zoom"]) < 0.15 else "✗ 有缩放"
    print(f"{name:24s} {truth:12s} {r['zoom']:+10.2f}  {ok}")

print("\n结论：如果推近给负、拉远给正，说明 zoom 判据方向是反的，")
print("      那么之前对 AI 视频的 zoom 结论也要整体取反。")
