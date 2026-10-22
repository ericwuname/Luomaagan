#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
AI 图 → 可编辑矢量（分层）
==========================

工作流（用户定）：AI 做美术指导，我做矢量精修。
本脚本负责"交接"这一步：把 AI 生成的位图，转成分层矢量。

为什么卡通风特别适合矢量化：
  卡通画是「平涂色块 + 黑描边」，本质就是矢量图。
  每个纯色区域 = 一个封闭形状 = 一个可编辑 path。
  照片不行（连续渐变），卡通风行。

输出：
  · xxx.svg   分层矢量（按色块堆叠）
  · xxx_layers.json  每层的颜色/面积/包围盒，便于程序化挑选要改的那层
"""
import json
import os
import sys

import numpy as np
from PIL import Image

try:
    import vtracer
except ImportError:
    print("需要 vtracer: pip install vtracer")
    sys.exit(1)


def analyze_layers(png_path, max_colors=14):
    """数出图里有哪些主色、各占多少面积 —— 用于给图层命名/分组"""
    im = Image.open(png_path).convert("RGB")
    a = np.asarray(im).reshape(-1, 3)
    # 简单量化
    q = (a // 24) * 24
    uniq, counts = np.unique(q, axis=0, return_counts=True)
    order = np.argsort(-counts)
    total = len(a)
    out = []
    for i in order[:max_colors]:
        c = uniq[i]
        out.append({
            "hex": "#%02X%02X%02X" % (c[0], c[1], c[2]),
            "ratio": round(counts[i] / total, 4),
        })
    return out


def to_svg(src, dst, **kw):
    """位图 → 分层 SVG"""
    opts = dict(
        colormode="color",
        hierarchical="stacked",   # 按堆叠顺序分层
        mode="spline",            # 用平滑曲线（不是多边形）
        filter_speckle=6,         # 去掉小于 6px 的噪点
        color_precision=6,        # 颜色精度
        layer_difference=16,      # 图层合并阈值
        corner_threshold=60,
        length_threshold=3.2,
        max_iterations=10,
        splice_threshold=45,
        path_precision=2,
    )
    opts.update(kw)
    vtracer.convert_image_to_svg_py(src, dst, **opts)
    return dst


def summarize(svg_path):
    """统计 SVG 里有多少 path、文件多大"""
    with open(svg_path, encoding="utf-8") as f:
        s = f.read()
    return {
        "paths": s.count("<path"),
        "bytes": len(s.encode("utf-8")),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python vectorize.py <图.png> [输出.svg]")
        sys.exit(0)
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + "_vec.svg"

    print(f"源图 {src}")
    layers = analyze_layers(src)
    print(f"主色 {len(layers)} 个：")
    for L in layers[:8]:
        print(f"   {L['hex']}  {L['ratio']*100:5.1f}%")

    to_svg(src, dst)
    info = summarize(dst)
    print(f"\n✓ {dst}")
    print(f"   {info['paths']} 个 path, {info['bytes']/1024:.0f} KB")

    meta = os.path.splitext(dst)[0] + "_layers.json"
    with open(meta, "w", encoding="utf-8") as f:
        json.dump({"source": os.path.basename(src), "colors": layers,
                   "paths": info["paths"]}, f, ensure_ascii=False, indent=2)
    print(f"✓ {meta}")

    # 转回 PNG 对比（检查矢量化损失）
    import cairosvg
    back = os.path.splitext(dst)[0] + "_back.png"
    cairosvg.svg2png(url=dst, write_to=back)
    print(f"✓ {back}（用于对比矢量化损失）")
