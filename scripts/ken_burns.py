#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
Ken Burns 精确运镜 —— 用程序生成"推近/拉远"，不靠 AI 猜

⛔ 为什么需要这个
   实测发现 Agnes 视频模型对 zoom 方向**完全不可靠，甚至反向**：
     · S2 要求推镜 → 实测拉远 zoom=-0.46
     · S5 要求推镜 → 实测拉远 zoom=-0.75
     · S7 要求拉远 → 实测推近 zoom=+0.27（反了）
   同一个 prompt 结构，S1 下摇修好了、S3 横移修好了，唯独 zoom 全军覆没。

✅ 解法
   **能用程序精确做的，就不要交给概率模型。**
   推近/拉远本质是几何变换——用 PIL 逐帧渲染，误差为零。

做法（保持画质）：
   拉远 = 先把原图放大到 `max_scale`，再逐帧缩到 1.0
   推近 = 从 1.0 逐帧放大到 `max_scale`
   每帧都从原图重采样，不会有累积模糊（这点比 ffmpeg zoompan 好）。
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image

FF = r"C:/Users/87465/.workbuddy/binaries/python/envs/aitv/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"
W, H, FPS = 1280, 704, 24


def ken_burns(src, dst, seconds=4.0, start_scale=1.0, end_scale=1.0,
              anchor=(0.5, 0.5), pre_upscale=1.0):
    """从一张图生成精确缩放的运动镜头。

    start_scale/end_scale: 相对「铺满画框」的缩放倍数（>1 放大，<1 露出更多）
    anchor: 缩放中心（0-1 归一化坐标）
    pre_upscale: 先把原图放大多少倍再采样（拉远时用 >1 减少锯齿）
    """
    im = Image.open(src).convert("RGB")
    if pre_upscale > 1.001:
        im = im.resize((int(im.width * pre_upscale), int(im.height * pre_upscale)),
                       Image.LANCZOS)

    n = int(round(seconds * FPS))
    ax, ay = anchor

    # 基准：把图等比铺满画框所需的尺寸
    base = max(W / im.width, H / im.height)
    frames = bytearray()

    for i in range(n):
        t = i / max(1, n - 1)
        # 缓入缓出（更接近真实运镜）
        e = t * t * (3 - 2 * t)
        s = start_scale + (end_scale - start_scale) * e
        cur_w = im.width * base * s
        cur_h = im.height * base * s
        left = (cur_w - W) * ax
        top = (cur_h - H) * ay
        # 目标区域（在放大后的图坐标里）
        x0 = min(max(0, left), cur_w - W) / (im.width * base)
        y0 = min(max(0, top), cur_h - H) / (im.height * base)
        x1 = x0 + W / (im.width * base * s)
        y1 = y0 + H / (im.height * base * s)
        box = (
            int(x0 * im.width), int(y0 * im.height),
            int(min(im.width, x1 * im.width)), int(min(im.height, y1 * im.height)),
        )
        if box[2] - box[0] < 2 or box[3] - box[1] < 2:
            box = (0, 0, im.width, im.height)
        crop = im.crop(box).resize((W, H), Image.LANCZOS)
        frames += crop.tobytes()

    subprocess.run([FF, "-y", "-v", "error",
                    "-f", "rawvideo", "-pix_fmt", "rgb24",
                    "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-an", dst],
                   input=bytes(frames), check=True)
    return dst


if __name__ == "__main__":
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EP = os.path.join(ROOT, "work", "ep01")
    OUT = os.path.join(EP, "clips_kb")
    os.makedirs(OUT, exist_ok=True)

    # 三个 zoom 类镜头的精确运镜
    JOBS = [
        # 镜号, 时长, start_scale, end_scale, anchor, pre_upscale
        ("S2_mirror_cap", 4.0, 1.00, 1.28, (0.50, 0.45), 1.35),   # 推近
        ("S5_lobby",      5.0, 1.00, 1.16, (0.46, 0.50), 1.25),   # 缓推
        ("S7_rooftop",    5.0, 1.30, 1.00, (0.50, 0.52), 1.45),   # 拉远
    ]
    for name, sec, s0, s1, anc, pu in JOBS:
        src = os.path.join(EP, name + ".png")
        dst = os.path.join(OUT, name + ".mp4")
        if not os.path.exists(src):
            print(f"  ! 缺 {name}.png")
            continue
        ken_burns(src, dst, sec, s0, s1, anc, pu)
        print(f"  ✓ {name}  {s0}→{s1}  {sec}s  {os.path.getsize(dst)//1024} KB")
    print(f"\n→ {OUT}")
