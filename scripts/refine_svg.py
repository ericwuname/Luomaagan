#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
矢量精修器
==========

工作流分工：AI 做美术指导（出形），我在这里做精确修改。

vtracer 转出来的 SVG 是「按颜色堆叠」的一堆 path，没有语义——
像一堆没打标签的零件。本工具给它们打标签：

  1. 解析每个 path 的 fill 颜色 + 包围盒（bbox）
  2. 按颜色分组、按面积排序
  3. 提供操作：改色 / 移动 / 缩放 / 删除 / 只保留某几组
  4. 支持「区域选择」：框选某个范围的 path（用来选中"耳朵"这种部件）
  5. 输出新 SVG + PNG

用法：
  python refine_svg.py list  in.svg                    # 看有哪些颜色组
  python refine_svg.py recolor in.svg out.svg --like "#904818" --to "#7A3F22"
  python refine_svg.py hide in.svg out.svg --likes "#FFFFFF"
  python refine_svg.py move in.svg out.svg --box x0,y0,x1,y1 --dx -12 --dy 0
  python refine_svg.py scale in.svg out.svg --box ... --sx 1.15 --sy 0.9
"""
import argparse
import json
import os
import re
import sys

import numpy as np

PATH_RE = re.compile(r"<path\b([^>]*)/?>", re.I)
ATTR_RE = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')


def parse_paths(svg_text):
    """拆出所有 path 及其属性"""
    out = []
    for i, m in enumerate(PATH_RE.finditer(svg_text)):
        attrs = dict(ATTR_RE.findall(m.group(1)))
        out.append({"i": i, "attrs": attrs, "raw": m.group(0),
                    "span": m.span()})
    return out


def bbox_of_d(d):
    """从 path 的 d 里粗算包围盒（取所有坐标点）"""
    nums = re.findall(r"-?\d+\.?\d*(?:[eE][-+]?\d+)?", d)
    vals = [float(x) for x in nums]
    if len(vals) < 2:
        return None
    xs = vals[0::2]
    ys = vals[1::2]
    return min(xs), min(ys), max(xs), max(ys)


def norm_color(c):
    if not c:
        return None
    c = c.strip().lower()
    m = re.match(r"#([0-9a-f]{6})", c)
    if m:
        return "#" + m.group(1).upper()
    m = re.match(r"#([0-9a-f]{3})", c)
    if m:
        h = m.group(1)
        return ("#" + "".join(ch * 2 for ch in h)).upper()
    return c


def load(svg_path):
    with open(svg_path, encoding="utf-8") as f:
        return f.read()


def build_index(svg_path):
    txt = load(svg_path)
    paths = parse_paths(txt)
    for p in paths:
        a = p["attrs"]
        p["fill"] = norm_color(a.get("fill"))
        p["bbox"] = bbox_of_d(a.get("d", "")) if "d" in a else None
        bb = p["bbox"]
        p["area"] = ((bb[2] - bb[0]) * (bb[3] - bb[1])) if bb else 0.0
        p["cx"] = (bb[0] + bb[2]) / 2 if bb else 0.0
        p["cy"] = (bb[1] + bb[3]) / 2 if bb else 0.0
    return txt, paths


def cmd_list(args):
    txt, paths = build_index(args.svg)
    groups = {}
    for p in paths:
        key = p["fill"] or "(none)"
        g = groups.setdefault(key, {"n": 0, "area": 0.0})
        g["n"] += 1
        g["area"] += p["area"]
    print(f"共 {len(paths)} 个 path，{len(groups)} 个颜色组：\n")
    for k, g in sorted(groups.items(), key=lambda kv: -kv[1]["area"]):
        print(f"  {k:10s}  {g['n']:4d} 个   覆盖面积 {g['area']:12.0f}")
    print("\n提示：path 数量多是因为纹理由无数小点组成。")
    print("     精修时用 --min-area 过滤掉碎点，或用 --box 框选区域。")


def _shift_d(d, dx, dy):
    """把 path d 里所有坐标平移（保守实现：只处理绝对坐标段）"""
    def repl(m):
        return f"{m.group(1)}{float(m.group(2)) + dx:.2f} {float(m.group(3)) + dy:.2f}"
    return re.sub(r"([MLCSTQ]\s*)(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)", repl, d)


def _scale_d(d, cx, cy, sx, sy):
    def repl(m):
        x = (float(m.group(2)) - cx) * sx + cx
        y = (float(m.group(3)) - cy) * sy + cy
        return f"{m.group(1)}{x:.2f} {y:.2f}"
    return re.sub(r"([MLCSTQ]\s*)(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)", repl, d)


def _select(paths, args):
    sel = []
    likes = None
    if args.like:
        likes = {norm_color(c) for c in
                 (args.like if isinstance(args.like, list) else [args.like])}
    for p in paths:
        if p["area"] < args.min_area:
            continue
        if likes and p["fill"] not in likes:
            continue
        if args.box:
            x0, y0, x1, y1 = [float(v) for v in args.box.split(",")]
            bb = p["bbox"]
            if not bb:
                continue
            # 中心点落在框内
            if not (x0 <= p["cx"] <= x1 and y0 <= p["cy"] <= y1):
                continue
        sel.append(p)
    return sel


def _rebuild(txt, sel, mutator, out):
    """按 sel 修改对应 path，写回"""
    pieces = []
    last = 0
    for p in sorted(sel, key=lambda q: q["span"][0]):
        s, e = p["span"]
        pieces.append(txt[last:s])
        pieces.append(mutator(p))
        last = e
    pieces.append(txt[last:])
    new = "".join(pieces)
    with open(out, "w", encoding="utf-8") as f:
        f.write(new)
    import cairosvg
    png = os.path.splitext(out)[0] + ".png"
    cairosvg.svg2png(bytestring=new.encode("utf-8"), write_to=png)
    return new, png


def cmd_recolor(args):
    txt, paths = build_index(args.svg)
    sel = _select(paths, args)
    print(f"选中 {len(sel)} 个 path")
    newc = norm_color(args.to)

    def mut(p):
        raw = p["raw"]
        if re.search(r'fill\s*=\s*"[^"]*"', raw):
            raw = re.sub(r'fill\s*=\s*"[^"]*"', f'fill="{newc}"', raw)
        else:
            raw = raw.replace("<path", f'<path fill="{newc}"', 1)
        return raw

    _, png = _rebuild(txt, sel, mut, args.out)
    print(f"✓ {args.out}\n✓ {png}")


def cmd_hide(args):
    txt, paths = build_index(args.svg)
    sel = _select(paths, args)
    print(f"选中 {len(sel)} 个 path")

    def mut(p):
        return p["raw"].replace("<path", '<path display="none"', 1)

    _, png = _rebuild(txt, sel, mut, args.out)
    print(f"✓ {args.out}\n✓ {png}")


def cmd_move(args):
    txt, paths = build_index(args.svg)
    sel = _select(paths, args)
    print(f"选中 {len(sel)} 个 path")

    def mut(p):
        raw = p["raw"]
        d = p["attrs"].get("d", "")
        nd = _shift_d(d, args.dx, args.dy)
        return raw.replace(d, nd, 1)

    _, png = _rebuild(txt, sel, mut, args.out)
    print(f"✓ {args.out}\n✓ {png}")


def cmd_scale(args):
    txt, paths = build_index(args.svg)
    sel = _select(paths, args)
    print(f"选中 {len(sel)} 个 path")
    if not sel:
        return
    cx = float(np.mean([p["cx"] for p in sel]))
    cy = float(np.mean([p["cy"] for p in sel]))
    print(f"中心 ({cx:.0f},{cy:.0f})  缩放 x{args.sx} y{args.sy}")

    def mut(p):
        raw = p["raw"]
        d = p["attrs"].get("d", "")
        nd = _scale_d(d, cx, cy, args.sx, args.sy)
        return raw.replace(d, nd, 1)

    _, png = _rebuild(txt, sel, mut, args.out)
    print(f"✓ {args.out}\n✓ {png}")


def cmd_report(args):
    """输出每个颜色组的位置分布，帮助定位部件"""
    txt, paths = build_index(args.svg)
    big = [p for p in paths if p["area"] >= args.min_area]
    big.sort(key=lambda p: -p["area"])
    print(f"面积 ≥ {args.min_area} 的 path：{len(big)} 个\n")
    print(f"{'#':>4} {'fill':10s} {'area':>10s}  bbox")
    for k, p in enumerate(big[:40]):
        bb = p["bbox"]
        print(f"{k:4d} {str(p['fill']):10s} {p['area']:10.0f}  "
              f"({bb[0]:.0f},{bb[1]:.0f})-({bb[2]:.0f},{bb[3]:.0f})")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("svg")
        p.add_argument("--like", nargs="*", default=None, help="按 fill 颜色筛选")
        p.add_argument("--box", default=None, help="x0,y0,x1,y1 按中心点框选")
        p.add_argument("--min-area", type=float, default=0.0, help="忽略碎点")

    p = sub.add_parser("list"); common(p); p.set_defaults(func=cmd_list)
    p = sub.add_parser("report"); common(p); p.set_defaults(func=cmd_report)

    p = sub.add_parser("recolor"); common(p)
    p.add_argument("out"); p.add_argument("--to", required=True)
    p.set_defaults(func=cmd_recolor)

    p = sub.add_parser("hide"); common(p)
    p.add_argument("out"); p.set_defaults(func=cmd_hide)

    p = sub.add_parser("move"); common(p)
    p.add_argument("out"); p.add_argument("--dx", type=float, default=0)
    p.add_argument("--dy", type=float, default=0)
    p.set_defaults(func=cmd_move)

    p = sub.add_parser("scale"); common(p)
    p.add_argument("out")
    p.add_argument("--sx", type=float, default=1.0)
    p.add_argument("--sy", type=float, default=1.0)
    p.set_defaults(func=cmd_scale)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
