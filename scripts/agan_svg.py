#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
阿甘 · 参数化角色生成器
=====================

为什么不用 AI 文生图：
  AI 是概率的——"耳朵短一点"它会整张重画，可能脸也变了、姿态也变了。
  改 10 次是 10 次掷骰子，不是 10 次迭代。

这个脚本的做法（查证自程序化角色设计实践）：
  "The avatar, the expression, and the animation are separate layers."
  "Adjust dimensions, roundness, position, rotation, perspective, colors."
  **每个部位是独立参数，改一个数字，1 秒出图，其他一切不变。**

参数都在 PARAMS 里。改完直接跑，输出 Svg + PNG。
"""
import math
import os
import sys

# ────────────────────────────────────────────────────────────
#  参数
# ────────────────────────────────────────────────────────────
PARAMS = dict(
    W=600, H=900,

    # 比例（1.0 = 基准）
    head_r=1.34,        # 头的大小
    face_len=0.34,      # 口鼻长度  ← 越大越像驴，越小越像马
    face_drop=0.92,     # 口鼻下垂角度
    neck_len=0.62,      # 脖子长度
    ear_len=1.05,       # 耳朵长度
    ear_w=0.86,         # 耳朵宽度
    ear_spread=1.15,    # 耳朵张开角度
    body_w=1.04,        # 身体宽度
    body_h=0.80,        # 身体长度
    waist=1.16,         # 腰的收束（>1 更细）
    leg_len=0.92,       # 腿长
    leg_w=1.18,         # 腿粗（<1 更细）
    arm_w=1.70,         # 臂粗
    hand_r=1.15,        # 手的大小

    # 姿态（S 曲线 / 不对称）
    lean=7.0,           # 整个上身的前倾角（度）
    hip_shift=10.0,     # 胯相对肩膀的横向偏移（负=向左）
    head_tilt=-4.0,     # 头倾斜（度）
    head_x=6.0,         # 头相对肩中心横向偏移
    ear_asym=0.86,      # 左耳长度 = 右耳 × 这个值（<1 就是两耳不等长）

    # 颜色
    fur="#A86236",
    fur_dark="#7A4326",
    fur_light="#D49469",
    muzzle="#E9C0A6",
    cloth="#EFE4C8",
    tie="#E8B21E",
    cap="#D9A62E",
    cap_dark="#B8871F",
    ink="#1A1410",
    paper="#F7F1E3",

    # 线宽
    lw_outer=7.0,
    lw_inner=3.2,
    lw_detail=2.0,

    # 开关
    show_cap=True,
    show_tie=True,
    show_ear_tape=True,
    show_bag=True,
)


def cr2bez(pts, closed=True, tension=1.0):
    """Catmull-Rom → 三次贝塞尔，返回 SVG path d。"""
    p = list(pts)
    if closed:
        n = len(p)
        seq = [p[-1]] + p + [p[0], p[1]]
    else:
        n = len(p)
        seq = [p[0]] + p + [p[-1]]
    d = [f"M {seq[1][0]:.2f} {seq[1][1]:.2f}"]
    for i in range(1, len(seq) - 2):
        p0, p1, p2, p3 = seq[i - 1], seq[i], seq[i + 1], seq[i + 2]
        c1x = p1[0] + (p2[0] - p0[0]) / 6.0 * tension
        c1y = p1[1] + (p2[1] - p0[1]) / 6.0 * tension
        c2x = p2[0] - (p3[0] - p1[0]) / 6.0 * tension
        c2y = p2[1] - (p3[1] - p1[1]) / 6.0 * tension
        d.append(f"C {c1x:.2f} {c1y:.2f} {c2x:.2f} {c2y:.2f} {p2[0]:.2f} {p2[1]:.2f}")
    if closed:
        d.append("Z")
    return " ".join(d)


def rot(pts, cx, cy, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * c - dy * s, cy + dx * s + dy * c))
    return out


class Agan:
    def __init__(self, **kw):
        self.p = {**PARAMS, **kw}
        self.parts = []

    # ---- 骨架基准点 ----
    def anchors(self):
        P = self.p
        cx = P["W"] / 2
        head_r = 74 * P["head_r"]
        # 头顶 → 脚底
        head_cy = 300
        neck_top = head_cy + head_r * 0.62
        neck_bot = neck_top + 66 * P["neck_len"]
        sh_y = neck_bot
        hip_y = sh_y + 250 * P["body_h"]
        foot_y = hip_y + 170 * P["leg_len"]
        return dict(cx=cx, head_cy=head_cy, head_r=head_r,
                    neck_top=neck_top, neck_bot=neck_bot,
                    sh_y=sh_y, hip_y=hip_y, foot_y=foot_y)

    def add(self, s):
        self.parts.append(s)

    # ---- 尾巴 ----
    def tail(self):
        P, A = self.p, self.anchors()
        cx, hip_y = A["cx"], A["hip_y"]
        bx = cx + P["hip_shift"]
        pts = [(bx + 30, hip_y - 20), (bx + 78, hip_y + 10),
               (bx + 96, hip_y + 82), (bx + 66, hip_y + 132)]
        d = cr2bez(pts, closed=False)
        self.add(f'<path d="{d}" fill="none" stroke="{P["ink"]}" '
                 f'stroke-width="{P["lw_outer"]*1.6}" stroke-linecap="round"/>')
        self.add(f'<path d="{d}" fill="none" stroke="{P["fur_dark"]}" '
                 f'stroke-width="{P["lw_outer"]*0.75}" stroke-linecap="round"/>')
        # 尾尖一撮
        tx, ty = bx + 66, hip_y + 132
        self.add(f'<ellipse cx="{tx}" cy="{ty}" rx="20" ry="26" fill="{P["fur_dark"]}" '
                 f'stroke="{P["ink"]}" stroke-width="{P["lw_inner"]}" '
                 f'transform="rotate(18 {tx} {ty})"/>')

    # ---- 腿 ----
    def legs(self):
        P, A = self.p, self.anchors()
        cx, hip_y, foot_y = A["cx"], A["hip_y"], A["foot_y"]
        hx = cx + P["hip_shift"]
        w = 15 * P["leg_w"]
        for side, dx_hip, dx_foot, knee in (
                (-1, -34, -46, -6), (1, 30, 44, 10)):
            x0 = hx + dx_hip
            x1 = hx + dx_foot
            kx = x0 + knee
            ky = (hip_y + foot_y) / 2 + 6
            pts = [(x0 - w, hip_y - 8), (x0 + w, hip_y - 8),
                   (kx + w * 0.9, ky), (x1 + w * 0.8, foot_y - 6),
                   (x1 - w * 0.8, foot_y - 6), (kx - w * 0.9, ky)]
            d = cr2bez(pts)
            self.add(f'<path d="{d}" fill="{P["fur"]}" stroke="{P["ink"]}" '
                     f'stroke-width="{P["lw_outer"]}" stroke-linejoin="round"/>')
            # 蹄
            self.add(f'<path d="{cr2bez([(x1 - w*0.9, foot_y-6), (x1 + w*0.9, foot_y-6), (x1 + w*1.15, foot_y+8), (x1 - w*1.15, foot_y+8)])}" '
                     f'fill="{P["ink"]}"/>')
            # 分趾
            self.add(f'<path d="M {x1:.1f} {foot_y-4} L {x1:.1f} {foot_y+8}" '
                     f'stroke="{P["paper"]}" stroke-width="2.2" opacity="0.55"/>')

    # ---- 躯干（S 曲线 + 腰收）----
    def torso(self):
        P, A = self.p, self.anchors()
        cx = A["cx"] + P["hip_shift"] * 0.5
        sh_y, hip_y = A["sh_y"], A["hip_y"]
        bw = 92 * P["body_w"]
        ww = bw * 0.62 / P["waist"]
        hw = bw * 0.78
        lean = P["lean"]
        left = [(cx - bw, sh_y + 6), (cx - ww, (sh_y + hip_y) / 2),
                (cx - hw, hip_y - 10), (cx, hip_y + 18)]
        right = [(cx + hw, hip_y - 10), (cx + ww, (sh_y + hip_y) / 2),
                 (cx + bw, sh_y + 6), (cx, sh_y - 16)]
        pts = rot(left + right, cx, sh_y, lean)
        self.add(f'<path d="{cr2bez(pts)}" fill="{P["fur"]}" stroke="{P["ink"]}" '
                 f'stroke-width="{P["lw_outer"]}" stroke-linejoin="round"/>')
        # 浅色腹部
        belly = rot([(cx - ww * 0.8, (sh_y + hip_y) / 2 - 10),
                     (cx - ww * 0.8, (sh_y + hip_y) / 2 + 80),
                     (cx + ww * 0.55, (sh_y + hip_y) / 2 + 90),
                     (cx + ww * 0.6, (sh_y + hip_y) / 2 - 20)],
                    cx, sh_y, lean)
        self.add(f'<path d="{cr2bez(belly)}" fill="{P["fur_light"]}" opacity="0.75"/>')

    # ---- 手臂（离开躯干，留负空间；一直一曲）----
    def arms(self):
        P, A = self.p, self.anchors()
        cx = A["cx"] + P["hip_shift"] * 0.5
        sh_y = A["sh_y"]
        lean = P["lean"]
        bw = 92 * P["body_w"]
        aw = 13 * P["arm_w"]
        # 左臂：向外张开，留出负空间
        L = rot([(cx - bw + 8, sh_y + 14), (cx - bw - 44, sh_y + 70),
                 (cx - bw - 58, sh_y + 130)], cx, sh_y, lean)
        # 右臂：抬起（举袋子）
        R = rot([(cx + bw + 2, sh_y + 14), (cx + bw + 46, sh_y - 30),
                 (cx + bw + 40, sh_y - 96)], cx, sh_y, lean)
        for idx, (pts, side) in enumerate(((L, -1), (R, 1))):
            # 一侧直、一侧曲 → 制造张力
            outer = [(x + aw * side, y) for x, y in pts]
            inner = [(x - aw * 0.55 * side, y + 3) for x, y in pts]
            d = cr2bez(outer, closed=False)
            d2 = cr2bez(list(reversed(inner)), closed=False)
            self.add(f'<path d="{d} L {inner[-1][0]:.1f} {inner[-1][1]:.1f} '
                     f'{d2[1:]} Z" fill="{P["fur"]}" stroke="{P["ink"]}" '
                     f'stroke-width="{P["lw_outer"]}" stroke-linejoin="round"/>')
            # 手
            hx, hy = pts[-1]
            self.add(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{18 * P["hand_r"]:.1f}" '
                     f'fill="{P["fur"]}" stroke="{P["ink"]}" stroke-width="{P["lw_outer"]}"/>')
            # 三指
            for k in (-1, 0, 1):
                ang = math.radians(90 + k * 34)
                fx = hx + math.cos(ang) * 15 * P["hand_r"]
                fy = hy + math.sin(ang) * 15 * P["hand_r"]
                self.add(f'<ellipse cx="{fx:.1f}" cy="{fy:.1f}" '
                         f'rx="{6.4*P["hand_r"]:.1f}" ry="{8.6*P["hand_r"]:.1f}" '
                         f'fill="{P["fur"]}" stroke="{P["ink"]}" stroke-width="{P["lw_inner"]}" '
                         f'transform="rotate({90+k*34} {fx:.1f} {fy:.1f})"/>')
        return R

    # ---- 头 ----
    def head(self):
        P, A = self.p, self.anchors()
        cx, cy, r = A["cx"] + P["head_x"], A["head_cy"], A["head_r"]
        tilt = P["head_tilt"]
        lean = P["lean"]

        # 脖子
        nb = A["neck_bot"]
        neck = rot([(cx - r * 0.42, cy + r * 0.45), (cx - r * 0.34, nb + 26),
                    (cx + r * 0.34, nb + 26), (cx + r * 0.42, cy + r * 0.45)],
                   cx, cy, lean)
        self.add(f'<path d="{cr2bez(neck)}" fill="{P["fur"]}" stroke="{P["ink"]}" '
                 f'stroke-width="{P["lw_outer"]}" stroke-linejoin="round"/>')

        # ── 耳朵（先画，压在头后）──
        self.ears(cx, cy, r, tilt, lean)

        # 颅骨（略长于圆，驴骡的脸偏长）
        skull = [(cx, cy - r * 1.02), (cx + r * 0.90, cy - r * 0.62),
                 (cx + r * 0.94, cy + r * 0.12), (cx + r * 0.58, cy + r * 0.66),
                 (cx, cy + r * 0.80), (cx - r * 0.58, cy + r * 0.66),
                 (cx - r * 0.94, cy + r * 0.12), (cx - r * 0.90, cy - r * 0.62)]
        skull = rot(skull, cx, cy, tilt)
        self.add(f'<path d="{cr2bez(skull)}" fill="{P["fur"]}" stroke="{P["ink"]}" '
                 f'stroke-width="{P["lw_outer"]}" stroke-linejoin="round"/>')

        # ── 口鼻（驴脸的核心：长）──
        fl = P["face_len"]
        fd = P["face_drop"]
        mz = [(cx - r * 0.44, cy + r * 0.30),
              (cx - r * 0.40, cy + r * (0.80 + 0.62 * fl) * fd),
              (cx + r * 0.06, cy + r * (1.10 + 0.78 * fl) * fd),
              (cx + r * 0.52, cy + r * (0.88 + 0.60 * fl) * fd),
              (cx + r * 0.52, cy + r * 0.34)]
        mz = rot(mz, cx, cy, tilt)
        self.add(f'<path d="{cr2bez(mz)}" fill="{P["muzzle"]}" stroke="{P["ink"]}" '
                 f'stroke-width="{P["lw_outer"]}" stroke-linejoin="round"/>')

        # 鼻孔
        for nx in (-0.16, 0.20):
            px = cx + r * nx
            py = cy + r * (1.02 + 0.66 * fl) * fd
            px, py = rot([(px, py)], cx, cy, tilt)[0]
            self.add(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{r*0.085:.1f}" '
                     f'ry="{r*0.065:.1f}" fill="{P["ink"]}" opacity="0.9"/>')

        # 嘴（笑）
        m0 = rot([(cx - r * 0.26, cy + r * (1.24 + 0.62 * fl) * fd)], cx, cy, tilt)[0]
        m1 = rot([(cx + r * 0.02, cy + r * (1.34 + 0.62 * fl) * fd)], cx, cy, tilt)[0]
        m2 = rot([(cx + r * 0.30, cy + r * (1.22 + 0.60 * fl) * fd)], cx, cy, tilt)[0]
        self.add(f'<path d="M {m0[0]:.1f} {m0[1]:.1f} Q {m1[0]:.1f} {m1[1]+4:.1f} '
                 f'{m2[0]:.1f} {m2[1]:.1f}" fill="none" stroke="{P["ink"]}" '
                 f'stroke-width="{P["lw_inner"]}" stroke-linecap="round"/>')

        # ── 眼睛（大，有眼神光）──
        for ex, ey, er in ((-0.42, 0.02, 0.315), (0.34, 0.02, 0.315)):
            px, py = rot([(cx + r * ex, cy + r * ey)], cx, cy, tilt)[0]
            self.add(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{r*er:.1f}" '
                     f'ry="{r*er*1.06:.1f}" fill="#FFFDF7" stroke="{P["ink"]}" '
                     f'stroke-width="{P["lw_inner"]}"/>')
            # 瞳孔（看向画面右）
            self.add(f'<circle cx="{px + r*0.055:.1f}" cy="{py + r*0.012:.1f}" '
                     f'r="{r*er*0.52:.1f}" fill="{P["ink"]}"/>')
            # 眼神光
            self.add(f'<circle cx="{px + r*0.10:.1f}" cy="{py - r*0.06:.1f}" '
                     f'r="{r*er*0.20:.1f}" fill="#FFFFFF"/>')
            # 上眼睑（半垂，显得有故事）
            lid = [(px - r * er, py - r * 0.02), (px, py - r * 0.20),
                   (px + r * er * 0.96, py - r * 0.02)]
            self.add(f'<path d="{cr2bez(lid, closed=False)}" fill="none" '
                     f'stroke="{P["ink"]}" stroke-width="{P["lw_outer"]*0.85}" '
                     f'stroke-linecap="round"/>')

        # 鬃毛（一小排，倒伏）
        for i in range(5):
            t = i / 4.0
            bx = cx + r * (0.10 + 0.30 * t)
            by = cy - r * (0.92 - 0.10 * t)
            bx, by = rot([(bx, by)], cx, cy, tilt)[0]
            self.add(f'<path d="M {bx:.1f} {by:.1f} q {8-4*t:.1f} {-14-4*t:.1f} '
                     f'{20-6*t:.1f} {-8-2*t:.1f}" fill="none" stroke="{P["ink"]}" '
                     f'stroke-width="{P["lw_outer"]*0.8}" stroke-linecap="round"/>')

    def ears(self, cx, cy, r, tilt, lean):
        P = self.p
        el, ew, sp = P["ear_len"], P["ear_w"], P["ear_spread"]
        for side, length_mul, tape in ((-1, P["ear_asym"], True), (1, 1.0, False)):
            base_x = cx + side * r * 0.52
            base_y = cy - r * 0.72
            ang = math.radians(side * (20 + 8 * sp))
            L = r * 1.30 * el * length_mul
            w = r * 0.30 * ew
            tipx = base_x + math.sin(ang) * L
            tipy = base_y - math.cos(ang) * L
            # 叶片：一侧直、一侧曲
            pts = [(base_x - w, base_y + 6),
                   (base_x - w * 0.55 + math.sin(ang) * L * 0.5, base_y - math.cos(ang) * L * 0.5),
                   (tipx - w * 0.28, tipy + 8),
                   (tipx + w * 0.34, tipy + 4),
                   (base_x + w * 0.62 + math.sin(ang) * L * 0.5, base_y - math.cos(ang) * L * 0.5),
                   (base_x + w, base_y + 6)]
            pts = rot(pts, cx, cy, tilt + lean * 0.4)
            self.add(f'<path d="{cr2bez(pts)}" fill="{P["fur"]}" stroke="{P["ink"]}" '
                     f'stroke-width="{P["lw_outer"]}" stroke-linejoin="round"/>')
            # 内耳
            inner = [(base_x - w * 0.42, base_y + 2),
                     (tipx - w * 0.12, tipy + 12),
                     (tipx + w * 0.16, tipy + 10),
                     (base_x + w * 0.40, base_y + 2)]
            inner = rot(inner, cx, cy, tilt + lean * 0.4)
            self.add(f'<path d="{cr2bez(inner)}" fill="{P["fur_light"]}" opacity="0.85"/>')
            if tape and P["show_ear_tape"]:
                # 黄胶带缠在中段
                tx = base_x + math.sin(ang) * L * 0.55
                ty = base_y - math.cos(ang) * L * 0.55
                tx, ty = rot([(tx, ty)], cx, cy, tilt + lean * 0.4)[0]
                tw, th = w * 1.35, 15
                self.add(f'<g transform="rotate({side*18} {tx:.1f} {ty:.1f})">'
                         f'<rect x="{tx-tw:.1f}" y="{ty-th/2:.1f}" width="{tw*2:.1f}" '
                         f'height="{th}" rx="4" fill="{P["tie"]}" stroke="{P["ink"]}" '
                         f'stroke-width="{P["lw_inner"]}"/></g>')

    # ---- 服饰 ----
    def clothes(self):
        P, A = self.p, self.anchors()
        cx = A["cx"] + P["hip_shift"] * 0.5
        sh_y, hip_y = A["sh_y"], A["hip_y"]
        lean = P["lean"]
        bw = 92 * P["body_w"]
        ww = bw * 0.62 / P["waist"]

        # 背心
        v = [(cx - bw * 0.92, sh_y + 16),
             (cx - ww * 1.02, (sh_y + hip_y) / 2 + 8),
             (cx - bw * 0.72, hip_y - 6),
             (cx + bw * 0.72, hip_y - 6),
             (cx + ww * 1.02, (sh_y + hip_y) / 2 + 8),
             (cx + bw * 0.92, sh_y + 16),
             (cx + bw * 0.46, sh_y - 4),
             (cx, sh_y + 34),
             (cx - bw * 0.46, sh_y - 4)]
        v = rot(v, cx, sh_y, lean)
        self.add(f'<path d="{cr2bez(v)}" fill="{P["cloth"]}" stroke="{P["ink"]}" '
                 f'stroke-width="{P["lw_outer"]}" stroke-linejoin="round"/>')

        if P["show_tie"]:
            t0 = rot([(cx - 10, sh_y + 30)], cx, sh_y, lean)[0]
            t1 = rot([(cx + 12, sh_y + 44)], cx, sh_y, lean)[0]
            t2 = rot([(cx + 8, sh_y + 150)], cx, sh_y, lean)[0]
            t3 = rot([(cx - 12, sh_y + 150)], cx, sh_y, lean)[0]
            self.add(f'<path d="{cr2bez([t0, t1, t2, t3])}" fill="{P["tie"]}" '
                     f'stroke="{P["ink"]}" stroke-width="{P["lw_inner"]}"/>')
            # 领带图案
            for k in range(3):
                yy = sh_y + 62 + k * 28
                a = rot([(cx - 9, yy)], cx, sh_y, lean)[0]
                b = rot([(cx + 9, yy + 12)], cx, sh_y, lean)[0]
                self.add(f'<circle cx="{(a[0]+b[0])/2:.1f}" cy="{(a[1]+b[1])/2:.1f}" '
                         f'r="5" fill="{P["ink"]}" opacity="0.65"/>')
            # 领结
            kn = rot([(cx, sh_y + 30)], cx, sh_y, lean)[0]
            self.add(f'<ellipse cx="{kn[0]:.1f}" cy="{kn[1]:.1f}" rx="13" ry="11" '
                     f'fill="{P["tie"]}" stroke="{P["ink"]}" stroke-width="{P["lw_inner"]}"/>')

    # ---- 帽子 ----
    def cap(self):
        if not self.p["show_cap"]:
            return
        P, A = self.p, self.anchors()
        cx, cy, r = A["cx"] + P["head_x"], A["head_cy"], A["head_r"]
        t = P["head_tilt"] + P["lean"] * 0.4
        crown = rot([(cx - r * 0.90, cy - r * 0.34),
                     (cx - r * 0.72, cy - r * 0.72),
                     (cx - r * 0.10, cy - r * 0.92),
                     (cx + r * 0.62, cy - r * 0.80),
                     (cx + r * 0.88, cy - r * 0.34)], cx, cy, t)
        self.add(f'<path d="{cr2bez(crown)}" fill="{P["cap"]}" stroke="{P["ink"]}" '
                 f'stroke-width="{P["lw_outer"]}" stroke-linejoin="round"/>')
        # 帽顶暗部（做旧）
        dark = rot([(cx - r * 0.60, cy - r * 0.70),
                    (cx - r * 0.08, cy - r * 0.88),
                    (cx + r * 0.55, cy - r * 0.78),
                    (cx + r * 0.30, cy - r * 0.60),
                    (cx - r * 0.20, cy - r * 0.62)], cx, cy, t)
        self.add(f'<path d="{cr2bez(dark)}" fill="{P["cap_dark"]}" opacity="0.75"/>')
        # 帽檐（压向画面左，遮一只眼）
        brim = rot([(cx - r * 0.94, cy - r * 0.30),
                    (cx - r * 1.58, cy - r * 0.16),
                    (cx - r * 1.50, cy + r * 0.04),
                    (cx - r * 0.86, cy - r * 0.06)], cx, cy, t)
        self.add(f'<path d="{cr2bez(brim)}" fill="{P["cap_dark"]}" stroke="{P["ink"]}" '
                 f'stroke-width="{P["lw_outer"]}" stroke-linejoin="round"/>')
        # 帽扣
        k = rot([(cx + r * 0.02, cy - r * 1.06)], cx, cy, t)[0]
        self.add(f'<circle cx="{k[0]:.1f}" cy="{k[1]:.1f}" r="6" fill="{P["ink"]}"/>')

    # ---- 外卖袋 ----
    def bag(self):
        if not self.p["show_bag"]:
            return
        P, A = self.p, self.anchors()
        cx = A["cx"] + P["hip_shift"] * 0.5
        sh_y = A["sh_y"]
        lean = P["lean"]
        bw = 92 * P["body_w"]
        hx, hy = rot([(cx + bw + 40, sh_y - 96)], cx, sh_y, lean)[0]
        bw2, bh2 = 46, 54
        self.add(f'<rect x="{hx-bw2/2:.1f}" y="{hy-bh2-6:.1f}" width="{bw2}" height="{bh2}" '
                 f'rx="6" fill="{P["cloth"]}" stroke="{P["ink"]}" '
                 f'stroke-width="{P["lw_outer"]}"/>')
        self.add(f'<path d="M {hx-14:.1f} {hy-bh2-6:.1f} q 14 -20 28 0" fill="none" '
                 f'stroke="{P["ink"]}" stroke-width="{P["lw_inner"]}"/>')

    # ---- 组装 ----
    def svg(self):
        P = self.p
        self.tail()
        self.legs()
        self.torso()
        arm_R = self.arms()
        self.head()
        self.clothes()
        self.cap()
        self.bag()
        body = "\n".join(self.parts)
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{P["W"]}" height="{P["H"]}"
     viewBox="0 0 {P["W"]} {P["H"]}">
  <defs>
    <pattern id="halftone" width="7" height="7" patternUnits="userSpaceOnUse">
      <circle cx="3.5" cy="3.5" r="1.5" fill="{P["ink"]}" opacity="0.13"/>
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="{P["paper"]}"/>
{body}
  <rect width="100%" height="100%" fill="url(#halftone)" opacity="0.5"/>
</svg>'''


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "agan.svg"
    a = Agan()
    s = a.svg()
    with open(out, "w", encoding="utf-8") as f:
        f.write(s)
    import cairosvg
    png = os.path.splitext(out)[0] + ".png"
    cairosvg.svg2png(bytestring=s.encode("utf-8"), write_to=png,
                     output_width=a.p["W"], output_height=a.p["H"])
    print(f"✓ {out}")
    print(f"✓ {png}")


if __name__ == "__main__":
    main()
