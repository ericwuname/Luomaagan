#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""把一批候选图拼成一张对比表，便于一眼判断"""
import os
import sys
import glob
from PIL import Image, ImageDraw


def build(paths, out, cols=4, tile=(300, 400)):
    ims = []
    for p in paths:
        try:
            im = Image.open(p).convert("RGB")
        except Exception:
            continue
        im.thumbnail(tile, Image.LANCZOS)
        ims.append((os.path.splitext(os.path.basename(p))[0], im))
    if not ims:
        print("没有可用的图")
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
        d.text((x, y), name, fill=(30, 30, 30))
        sheet.paste(im, (x + (tile[0] - im.size[0]) // 2, y + 18))
    sheet.save(out)
    print(f"✓ {out}  {len(ims)} 张")


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outdir = os.path.join(base, "work", "char", "_sheets")
    os.makedirs(outdir, exist_ok=True)
    batches = sorted(glob.glob(os.path.join(base, "work", "char", "batch_*")))
    allp = []
    for b in batches:
        allp += sorted(glob.glob(os.path.join(b, "*.png")))
    build(allp, os.path.join(outdir, "ALL_candidates.png"), cols=4)
    if batches:
        last = batches[-1]
        build(sorted(glob.glob(os.path.join(last, "*.png"))),
              os.path.join(outdir, "LATEST.png"), cols=4)
