#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
剪影测试 —— 把交接书的主观验收标准变成可执行的检查

验收标准（交接书 4.2 / 五.第一步）：
  "将角色图涂成全黑剪影并缩小至头像尺寸，仍可一眼识别出「小骡子 + 缺耳尖」"

本工具做三件事：
  1. 抠出角色（背景是纯色 cream，用颜色距离分离）
  2. 生成全黑剪影，缩到 256 / 128 / 64 / 48 四个尺寸
  3. 拼成一张对比图 —— 用户一眼判断，不用自己动手

同时量化三个可测指标（用于横向比较多个候选）：
  · 宽高比     —— 判断"瘦小"（<0.75 才算瘦）
  · 耳尖凹陷   —— 在顶部轮廓里检测局部曲率极小值（缺角的存在性证据）
  · 轮廓复杂度 —— 周长²/面积，太低=糊成一坨，太高=碎
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def extract_silhouette(img_path, bg_tol=42):
    """抠出角色，返回 bool mask（True=角色）"""
    im = Image.open(img_path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    h, w, _ = a.shape
    # 背景采样：取四角 + 四边中点
    pts = [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3),
           (w // 2, 2), (w // 2, h - 3), (2, h // 2), (w - 3, h // 2)]
    samples = np.array([a[y, x] for x, y in pts])
    bg = np.median(samples, axis=0)
    dist = np.sqrt(((a - bg) ** 2).sum(axis=2))
    mask = dist > bg_tol
    # 去掉边缘噪点：只保留较大连通域（用简单形态学近似）
    m = Image.fromarray((mask * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MedianFilter(5))
    m = m.filter(ImageFilter.MaxFilter(3))
    m = m.filter(ImageFilter.MinFilter(3))
    arr = np.asarray(m) > 127
    if arr.sum() < (h * w) * 0.01:
        # 兜底：用亮度差异
        gray = a.mean(axis=2)
        arr = gray < (gray.mean() - 12)
    return arr


def bbox_of(mask):
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return None
    return xs.min(), ys.min(), xs.max(), ys.max()


def split_views(mask, min_gap_frac=0.02):
    """把三视图按列空隙切成多个单视图。
    ⚠️ 三视图整张直接做剪影测试是错的——宽高比会是整张图的，
       耳尖凹陷会把几个头的鬃毛全算进去。必须先切分。"""
    h, w = mask.shape
    cols = mask.sum(axis=0)
    thresh = max(1, int(h * 0.01))
    empty = cols <= thresh
    if empty.all() or not empty.any():
        return [(0, w - 1)]
    # 找连续的非空区
    segs = []
    i = 0
    min_gap = max(3, int(w * min_gap_frac))
    while i < w:
        if empty[i]:
            i += 1
            continue
        j = i
        while j < w and not empty[j]:
            j += 1
        segs.append((i, j - 1))
        i = j
    # 合并间隔太小的（同一角色被切开）
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < min_gap:
            merged[-1] = (merged[-1][0], s[1])
        else:
            merged.append(list(s))
    # 过滤太窄的（噪点）
    merged = [tuple(m) for m in merged if (m[1] - m[0]) > w * 0.06]
    return merged or [(0, w - 1)]


def analyze(mask):
    """量化指标"""
    bb = bbox_of(mask)
    if not bb:
        return {}
    x0, y0, x1, y1 = bb
    bw, bh = x1 - x0 + 1, y1 - y0 + 1
    sub = mask[y0:y1 + 1, x0:x1 + 1]
    area = int(sub.sum())
    # 周长
    p = 0
    p += int(sub[0, :].sum() + sub[-1, :].sum() + sub[:, 0].sum() + sub[:, -1].sum())
    p += int((sub[1:, :] != sub[:-1, :]).sum() + (sub[:, 1:] != sub[:, :-1]).sum())
    # 每列顶部轮廓（找耳尖凹陷）
    tops = []
    for cx in range(sub.shape[1]):
        col = np.where(sub[:, cx])[0]
        tops.append(col[0] if len(col) else sub.shape[0])
    tops = np.array(tops, dtype=np.float32)
    # 平滑后找局部极大（y 越大 = 越凹）
    k = max(3, len(tops) // 60)
    ker = np.ones(k) / k
    ts = np.convolve(tops, ker, mode="same")
    dips = 0
    for i in range(k, len(ts) - k):
        if ts[i] >= ts[i - k:i].max() and ts[i] >= ts[i + 1:i + 1 + k].max():
            if ts[i] - min(ts[i - k:i].min(), ts[i + 1:i + 1 + k].min()) > sub.shape[0] * 0.05:
                dips += 1
    return dict(w=bw, h=bh, ratio=bw / max(1, bh), area=area,
                perimeter=p, compact=(p * p) / max(1, area),
                top_dips=dips, fill=area / max(1, bw * bh))


def make_silhouette_img(mask, color=(18, 18, 20)):
    out = np.zeros(mask.shape + (3,), dtype=np.uint8)
    out[...] = (250, 248, 242)
    out[mask] = color
    return Image.fromarray(out)


def build_sheet(img_path, out_path, sizes=(256, 128, 64, 48), pad=14):
    full = extract_silhouette(img_path)
    views = split_views(full)
    print(f"    切出 {len(views)} 个视图")

    results = []
    for vi, (vx0, vx1) in enumerate(views):
        mask = np.zeros_like(full)
        mask[:, vx0:vx1 + 1] = full[:, vx0:vx1 + 1]
        bb = bbox_of(mask)
        if not bb:
            continue
        x0, y0, x1, y1 = bb
        mg = 8
        x0, y0 = max(0, x0 - mg), max(0, y0 - mg)
        x1 = min(mask.shape[1] - 1, x1 + mg)
        y1 = min(mask.shape[0] - 1, y1 + mg)
        dmask = mask[y0:y1 + 1, x0:x1 + 1]
        stat = analyze(dmask)
        stat["view"] = vi
        results.append((dmask, (x0, y0, x1, y1), stat))

    if not results:
        print(f"  ✗ 抠不出角色：{img_path}")
        return None

    # 用第一个视图（正面）出对比图
    dmask, box, stat = results[0]
    sil = make_silhouette_img(dmask)
    orig = Image.open(img_path).convert("RGB").crop(box)

    tiles = [("原图", orig)]
    for s in sizes:
        w0, h0 = sil.size
        sc = s / max(w0, h0)
        nw, nh = max(1, int(w0 * sc)), max(1, int(h0 * sc))
        tiles.append((f"剪影 {s}px", sil.resize((nw, nh), Image.LANCZOS)))

    H = max(t[1].size[1] for t in tiles) + 40
    W = sum(t[1].size[0] for t in tiles) + pad * (len(tiles) + 1)
    sheet = Image.new("RGB", (W, H), (238, 236, 230))
    d = ImageDraw.Draw(sheet)
    x = pad
    for name, im in tiles:
        sheet.paste(im, (x, 30 + (H - 40 - im.size[1]) // 2))
        d.text((x, 10), name, fill=(40, 40, 40))
        x += im.size[0] + pad
    d.text((10, H - 16),
           f"正面视图  宽高比 {stat['ratio']:.2f} (<0.75=瘦)   "
           f"耳尖凹陷 {stat['top_dips']} 处   "
           f"轮廓复杂度 {stat['compact']:.1f}   共{len(views)}视图",
           fill=(30, 30, 30))
    sheet.save(out_path)
    stat["n_views"] = len(views)
    return stat


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python silhouette_test.py <图1> [图2 ...]")
        sys.exit(0)
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outdir = os.path.join(base, "work", "char", "_silhouette")
    os.makedirs(outdir, exist_ok=True)
    for p in sys.argv[1:]:
        name = os.path.splitext(os.path.basename(p))[0]
        out = os.path.join(outdir, f"SIL_{name}.png")
        st = build_sheet(p, out)
        if st:
            ok_ratio = "✓" if st["ratio"] < 0.75 else "✗"
            ok_dip = "✓" if st["top_dips"] >= 1 else "✗"
            print(f"  {name:28s} 宽高比 {st['ratio']:.2f}{ok_ratio}  "
                  f"耳尖凹陷 {st['top_dips']}{ok_dip}  → {out}")
