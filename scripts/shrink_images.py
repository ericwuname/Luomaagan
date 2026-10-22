#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
推送前压缩图片 —— 原始候选图动辄 4MB，仓库会到 127MB。
压到最长边 1024 + PNG 优化，体积约降到 1/6，设计判读完全够用。

原始大图留在本地（已 .gitignore），仓库里只放压缩版。
"""
import os
import sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX = 1024


def shrink(p, dst=None):
    im = Image.open(p)
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGB")
    w, h = im.size
    if max(w, h) > MAX:
        s = MAX / max(w, h)
        im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    out = dst or p
    if out.lower().endswith(".png"):
        im.save(out, "PNG", optimize=True)
    else:
        im.save(out, "JPEG", quality=88, optimize=True)
    return os.path.getsize(out), im.size


if __name__ == "__main__":
    targets = []
    for base, _, files in os.walk(ROOT):
        if ".git" in base:
            continue
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                targets.append(os.path.join(base, f))
    total_before = sum(os.path.getsize(p) for p in targets)
    n = 0
    for p in targets:
        try:
            sz, dim = shrink(p)
            n += 1
        except Exception as e:
            print(f"  跳过 {os.path.basename(p)}: {str(e)[:60]}")
    total_after = sum(os.path.getsize(p) for p in targets)
    print(f"✓ 压缩 {n} 张")
    print(f"  {total_before/1024/1024:.1f} MB → {total_after/1024/1024:.1f} MB")
