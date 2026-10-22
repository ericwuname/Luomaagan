#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
首帧方案对比 —— 用参考图 vs 纯文字，测速度和一致性

⛔ 问题：传 I2I 参考图（864×1152）后，单张要 575 秒（9.6 分钟），
   26 张要 4 小时。**不可接受。**

要回答的问题：
  1. 缩小参考图（480×640）能不能显著提速？
  2. 完全不用参考图、只靠精确文字描述，角色还像不像？
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01c")
TEST = os.path.join(EP, "_test")
os.makedirs(TEST, exist_ok=True)
HERO = os.path.join(ROOT, "assets", "hero", "AGAN_MASTER_2k.png")

# 缩小参考图
small = os.path.join(TEST, "hero_480.png")
if not os.path.exists(small):
    im = Image.open(HERO).convert("RGB")
    im.thumbnail((480, 480), Image.LANCZOS)
    im.save(small, "PNG", optimize=True)
print(f"参考图 {im.size}  {os.path.getsize(small)//1024} KB")

STYLE = ("vintage American cartoon style, thick bold black ink outlines, "
         "flat solid colors, visible halftone dot texture, "
         "warm nostalgic picture-book mood, cinematic 16:9 composition")

DESC = ("**a small cartoon hinny delivery courier** — "
        "**slate blue-grey fur** (muted blue-grey, NOT plain donkey grey), "
        "**a cream-white squarish muzzle** occupying the lower half of the face, "
        "with two black oval nostrils on its top edge, "
        "**very large round eyes** with big white sclera, black pupils and white catchlights, "
        "**two long upright ears** with pale grey inner surfaces and halftone dots, "
        "a simple thin curved line as a smile, "
        "**an amber-orange zipped vest**, **an orange backpack**, "
        "slate-grey three-fingered hands, black hooves, "
        "a thin tail with a black tuft at the tip, ")

SHOT = ("medium shot, inside a tiny rented room at dawn, " + DESC +
        "sitting on the edge of a narrow bed pulling on his amber vest, "
        "a small homemade paper flag in one hand, a kettle and a cracked mirror behind him, "
        "one warm shaft of light across the wall, " + STYLE)

TESTS = [
    ("A_ref480", dict(init_images=[small])),
    ("B_noref",  dict()),
]

if __name__ == "__main__":
    for tag, kw in TESTS:
        out = os.path.join(TEST, tag + ".png")
        if os.path.exists(out) and os.path.getsize(out) > 200000:
            print(f"  · {tag} 已存在")
            continue
        print(f"  → {tag} ...", flush=True)
        try:
            t0 = time.time()
            agnes.gen_image(SHOT, size="2K", ratio="16:9", save_to=out, **kw)
            dt = time.time() - t0
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
        except Exception as e:
            print(f"    ✗ {str(e)[:160]}", flush=True)
