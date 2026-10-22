#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
手机屏幕镜头 · 程序化动画

为什么不交给 AI 视频：
  · 屏幕文字 AI 一定会改糊、改乱
  · 这 4 镜要传达的是**精确信息**（9996 / 9997 / 9999 / 10000），一个字都不能错
  · 程序逐帧渲染，每一帧都清晰，且可以做"通知弹出"这种精确动效

四种动效：
  S01 今日已完成 9996 → 极慢推近（呼吸）
  S04 新订单 9997    → **从上方滑入 + 轻微回弹**（像手机真的响了）
  S20 第 9999 单     → 缓慢推近 + 对勾轻微跳动
  S22 第 10000 单    → **滑入 + 橙色高亮闪一下**（里程碑的分量）
"""
import math
import os
import subprocess

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01c")
OUT = os.path.join(EP, "clips")
os.makedirs(OUT, exist_ok=True)

FF = (r"C:/Users/87465/.workbuddy/binaries/python/envs/aitv/Lib/"
      r"site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe")
W, H, FPS = 1280, 704, 24


def ease_out(t):
    return 1 - (1 - t) ** 3


def ease_io(t):
    return t * t * (3 - 2 * t)


def render(src, dst, seconds, mode):
    base = Image.open(src).convert("RGB")
    bw, bh = base.size
    n = int(round(seconds * FPS))
    frames = bytearray()

    for i in range(n):
        t = i / max(1, n - 1)
        e = ease_io(t)

        # 缩放（缓慢推近 1.00 → 1.06）
        s = 1.0 + 0.06 * e
        cw, ch = W / s, H / s
        # 基准铺满
        scale = max(W / bw, H / bh)
        bw2, bh2 = int(bw * scale), int(bh * scale)
        img = base.resize((bw2, bh2), Image.LANCZOS)

        # 从中心裁出
        cx, cy = bw2 / 2, bh2 / 2
        box = (int(cx - cw / 2), int(cy - ch / 2),
               int(cx + cw / 2), int(cy + ch / 2))
        box = (max(0, box[0]), max(0, box[1]),
               min(bw2, box[2]), min(bh2, box[3]))
        crop = img.crop(box).resize((W, H), Image.LANCZOS)

        arr = np.asarray(crop).astype(np.float32)

        if mode == "slide":
            # 通知从上方滑入 + 回弹
            p = min(1.0, t / 0.45)
            k = ease_out(p)
            bounce = math.sin(p * math.pi) * 0.035
            shift = int((k - 1 + bounce * (1 - p)) * H * 0.5)
            if shift != 0:
                arr = np.roll(arr, shift, axis=0)
                if shift > 0:
                    arr[:shift] = arr[:shift] * 0.35 + 240 * 0.65
            # 末尾亮度轻微恢复
            if t > 0.55:
                glow = math.sin((t - 0.55) / 0.45 * math.pi) * 0.06
                arr = arr * (1 + glow)

        elif mode == "flash":
            # 里程碑：橙色闪一下
            p = min(1.0, t / 0.5)
            k = ease_out(p)
            bounce = math.sin(p * math.pi) * 0.04
            shift = int((k - 1 + bounce * (1 - p)) * H * 0.5)
            if shift != 0:
                arr = np.roll(arr, shift, axis=0)
                if shift > 0:
                    arr[:shift] = arr[:shift] * 0.30 + 240 * 0.70
            # 闪光
            if 0.32 < t < 0.62:
                g = math.sin((t - 0.32) / 0.30 * math.pi) * 0.16
                arr = arr + np.array([g * 255, g * 190, g * 40], dtype=np.float32)

        elif mode == "pulse":
            # 对勾轻微跳动
            if 0.15 < t < 0.55:
                p = (t - 0.15) / 0.40
                g = math.sin(p * math.pi * 2) * math.exp(-p * 3) * 0.05
                arr = arr * (1 + g)

        arr = np.clip(arr, 0, 255).astype(np.uint8)
        frames += arr.tobytes()

    subprocess.run([FF, "-y", "-v", "error",
                    "-f", "rawvideo", "-pix_fmt", "rgb24",
                    "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-an", dst],
                   input=bytes(frames), check=True)
    return dst


JOBS = [
    ("S01_phone", 6.0, "push"),
    ("S04_phone", 5.0, "slide"),
    ("S20_phone", 5.0, "pulse"),
    ("S22_phone", 5.0, "flash"),
]

if __name__ == "__main__":
    for name, sec, mode in JOBS:
        src = os.path.join(EP, name + ".png")
        dst = os.path.join(OUT, name + ".mp4")
        if not os.path.exists(src):
            print(f"  ! 缺 {name}.png")
            continue
        render(src, dst, sec, mode)
        print(f"  ✓ {name}  {mode:6s} {sec}s  {os.path.getsize(dst)//1024} KB")
    print(f"\n→ {OUT}")
