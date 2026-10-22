#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
矢量化 v2 —— 关键是「少而干净」的色块，不是「完整还原」

v1 的错：color_precision=6 + layer_difference=16 → 812 个颜色组
       每个细微色差、每个网点都单独成层，根本没法编辑。

目标：**10-20 个色块**，每个色块对应一个可识别的部件（头/耳/身体/背心/领带）。
网点纹理不要了——矢量图不需要网点，后期用 SVG pattern 叠就行。

调参方向：
  · color_precision  ↓  少认几级颜色
  · layer_difference ↑  相似颜色合并
  · filter_speckle   ↑  丢小噪点
"""
import json
import os
import sys

import numpy as np
from PIL import Image
import vtracer


def prep(src, dst, max_side=1100):
    """先把图缩到合理尺寸，并把相近颜色压平（减少色阶）"""
    im = Image.open(src).convert("RGB")
    w, h = im.size
    if max(w, h) > max_side:
        s = max_side / max(w, h)
        im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    # 量化到 24 级，压掉细微色差
    q = im.quantize(colors=22, method=Image.MEDIANCUT, dither=Image.NONE)
    out = q.convert("RGB")
    out.save(dst)
    return out.size


def run(src, dst, speckle=24, layer_diff=64, precision=3):
    vtracer.convert_image_to_svg_py(
        src, dst,
        colormode="color",
        hierarchical="stacked",
        mode="spline",
        filter_speckle=speckle,
        color_precision=precision,
        layer_difference=layer_diff,
        corner_threshold=70,
        length_threshold=4.0,
        max_iterations=12,
        splice_threshold=50,
        path_precision=2,
    )


def count_groups(svg_path):
    import re
    with open(svg_path, encoding="utf-8") as f:
        s = f.read()
    fills = re.findall(r'fill="(#[0-9A-Fa-f]{6})"', s)
    return s.count("<path"), len(set(fills)), len(s.encode()) / 1024


if __name__ == "__main__":
    src = sys.argv[1]
    stem = os.path.splitext(src)[0]
    flat = stem + "_flat.png"
    size = prep(src, flat)
    print(f"预处理 → {flat}  {size[0]}x{size[1]}  22 色")

    best = None
    for speckle, ld, prec in ((24, 64, 3), (40, 96, 3), (60, 128, 2)):
        dst = f"{stem}_v2_{speckle}_{ld}.svg"
        run(flat, dst, speckle, ld, prec)
        npath, ng, kb = count_groups(dst)
        print(f"  speckle={speckle:3d} layerdiff={ld:3d} prec={prec} → "
              f"{npath:4d} path, {ng:3d} 色组, {kb:6.0f} KB")
        if best is None or abs(ng - 14) < abs(best[1] - 14):
            best = (dst, ng, npath)

    print(f"\n最接近 14 色组的：{best[0]}  ({best[1]} 色组, {best[2]} path)")

    import cairosvg
    back = os.path.splitext(best[0])[0] + "_back.png"
    cairosvg.svg2png(url=best[0], write_to=back)
    print(f"✓ {back}")
