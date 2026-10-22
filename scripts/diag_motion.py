#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
运动方向诊断 —— 量化每个镜头的实际运镜方向

用户说"运动方向不对"。不猜，量出来：
  1. 帧间差异的**重心位移** → 画面整体往哪移动
  2. **缩放强度** → 是推近(dolly in)还是拉远(pull back)
  3. **垂直位移** → 上摇还是下摇

方法：连续帧做灰度差，把差异图当成"运动能量"，算它的质心漂移。
"""
import os
import subprocess
import sys

import numpy as np

FF = r"C:/Users/87465/.workbuddy/binaries/python/envs/aitv/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"
W, H = 320, 176

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIPS = os.path.join(ROOT, "work", "ep01", "clips")

# 分镜要求（Gemini 的分镜表）
WANT = {
 "S1_alley_dawn": "下摇（tilt DOWN）",
 "S2_mirror_cap": "推镜（push in）",
 "S3_scooter":    "侧跟平移（向右 / 向画面前方）",
 "S4_bridge":     "低角度仰拍，动态抓拍",
 "S5_lobby":      "仰拍 + 正反打",
 "S6_elevator":   "固定机位（几乎不动）",
 "S7_rooftop":    "拉远（pull back / crane out）",
}


def frames(p):
    raw = subprocess.run([FF, "-v", "error", "-i", p,
                          "-vf", f"scale={W}:{H}", "-pix_fmt", "gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    n = len(raw) // (W * H)
    return np.frombuffer(raw[:n * W * H], dtype=np.uint8).reshape(n, H, W).astype(np.float32)


def analyze(p):
    x = frames(p)
    if len(x) < 3:
        return None
    d = np.abs(np.diff(x, axis=0))          # 每帧的运动能量图
    # 质心
    cxs, cys, energy = [], [], []
    ys, xs = np.mgrid[0:H, 0:W]
    for i in range(len(d)):
        e = d[i]
        s = e.sum()
        if s < 1e-3:
            continue
        cxs.append((e * xs).sum() / s / W)
        cys.append((e * ys).sum() / s / H)
        energy.append(s / (W * H))
    if not cxs:
        return None
    nx = np.array(cxs); ny = np.array(cys)
    # 线性趋势（画面能量中心的漂移方向）
    t = np.arange(len(nx))
    slope_x = np.polyfit(t, nx, 1)[0] if len(nx) > 2 else 0.0
    slope_y = np.polyfit(t, ny, 1)[0] if len(ny) > 2 else 0.0

    # 缩放：边缘区域能量 / 中心区域能量 的比值变化
    # ⛔ 方向已校准（scripts/calib_motion.py）：
    #    推近 1.00→1.60 时该比值**下降**（实测 -1.08），
    #    拉远 1.60→1.00 时**上升**（实测 +1.08）。
    #    所以判据要取负号：**edge/center 下降 = 推近**。
    #    这个方向与直觉相反，原因：放大时画面内容被推出边缘，
    #    边缘区变成"新进入的内容"，帧间差分反而变小。
    m = H // 4
    edge_by_frame = np.mean([
        d[:, :m, :].mean(axis=(1, 2)),
        d[:, -m:, :].mean(axis=(1, 2)),
        d[:, :, :m].mean(axis=(1, 2)),
        d[:, :, -m:].mean(axis=(1, 2)),
    ], axis=0)
    center = d[:, m:-m, m:-m].mean(axis=(1, 2)) if W > 2 * m else d.mean(axis=(1, 2))
    ratio = edge_by_frame / (center + 1e-6)
    raw = np.polyfit(np.arange(len(ratio)), ratio, 1)[0] if len(ratio) > 2 else 0.0
    zoom_slope = -raw          # ← 取负，校准后的方向

    return dict(
        n=len(x),
        drift_x=slope_x * len(nx),     # 全程横移（归一化画面宽）
        drift_y=slope_y * len(ny),
        zoom=zoom_slope * len(ratio),
        energy=float(np.mean(energy)),
    )


def describe(r):
    parts = []
    if abs(r["drift_x"]) < 0.04:
        parts.append("横向几乎不动")
    elif r["drift_x"] > 0:
        parts.append("能量右移（画面内容向左流）")
    else:
        parts.append("能量左移（画面内容向右流）")

    if abs(r["drift_y"]) < 0.04:
        parts.append("纵向几乎不动")
    elif r["drift_y"] > 0:
        parts.append("下摇（tilt DOWN）")
    else:
        parts.append("上摇（tilt UP）")

    if abs(r["zoom"]) < 0.15:
        parts.append("无缩放")
    elif r["zoom"] > 0:
        parts.append("推近★（边缘运动增强）")
    else:
        parts.append("拉远（边缘运动减弱）")
    return " / ".join(parts)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        CLIPS = sys.argv[1]
    print(f"{'镜头':22s} {'分镜要求':26s} 实测")
    print("-" * 100)
    for name in WANT:
        p = os.path.join(CLIPS, name + ".mp4")
        if not os.path.exists(p):
            print(f"{name:22s} {'（缺文件）':26s}")
            continue
        r = analyze(p)
        if not r:
            continue
        print(f"{name:22s} {WANT[name]:26s} {describe(r)}")
        print(f"{'':22s} {'':26s} dx={r['drift_x']:+.3f} dy={r['drift_y']:+.3f} "
              f"zoom={r['zoom']:+.2f} 能量={r['energy']:.4f}")
