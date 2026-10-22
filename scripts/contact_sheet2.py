#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""把指定批次的图拼成对比表（支持多选）"""
import os
import sys
import glob
from PIL import Image, ImageDraw


def build(paths, out, cols=4, tile=(320, 420)):
    ims = []
    for p in paths:
        try:
            im = Image.open(p).convert("RGB")
        except Exception:
            continue
        im.thumbnail(tile, Image.LANCZOS)
        ims.append((os.path.splitext(os.path.basename(p))[0], im))
    if not ims:
        return
    rows = (len(ims) + cols - 1) // cols
    W = cols * (tile[0] + 12) + 12
    H = rows * (tile[1] + 34) + 12
    sheet = Image.new("RGB", (W, H), (245, 243, 238))
    d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(ims):
        r, c = divmod(i, cols)
        x = 12 + c * (tile[0] + 12)
        y = 12 + r * (tile[1] + 34)
        d.text((x + 4, y + 2), name, fill=(20, 20, 20))
        sheet.paste(im, (x + (tile[0] - im.size[0]) // 2, y + 18))
    sheet.save(out)
    print(f"✓ {out}  {len(ims)} 张")


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outdir = os.path.join(base, "work", "char", "_sheets")
    os.makedirs(outdir, exist_ok=True)
    if len(sys.argv) > 2:
        build(sys.argv[2:], sys.argv[1])
    else:
        batches = sorted(glob.glob(os.path.join(base, "work", "char", "batch_*")))
        # 只取 v4 + v5 两批（形状语言实验）
        targets = []
        for b in batches[-2:]:
            targets += sorted(glob.glob(os.path.join(b, "*.png")))
        build(targets, os.path.join(outdir, "SHAPE_v4v5.png"), cols=4)
        allp = []
        for b in batches:
            allp += sorted(glob.glob(os.path.join(b, "*.png")))
        build(allp, os.path.join(outdir, "ALL_candidates.png"), cols=5)
