#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP02 手机屏幕镜头 · 程序渲染

两个镜头：
  01_phone_note  订单备注「千万别按门铃！我家鹦鹉会学，学会就停不下来。」
                 ← **全片前 3 秒建立规则，糊了整集就废了**
  15_silent      静音模式界面（铃铛被斜线划过）
                 ← 阿甘用来证明"我手机调了静音"

⛔ 为什么必须程序画
   AI 生成中文必然乱码。而这两个镜头承担"规则建立"和"证据澄清"两个关键功能，
   文字一糊，观众就看不懂阿甘为什么不敢按门铃、也看不懂他怎么自证清白。
"""
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep02")
OUT = os.path.join(EP, "clips")
os.makedirs(OUT, exist_ok=True)

W, H, FPS = 1280, 704, 24
FF = (r"C:/Users/87465/.workbuddy/binaries/python/envs/aitv/Lib/"
      r"site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe")

CREAM = (240, 224, 192)
DARK = (26, 20, 16)
ORANGE = (240, 160, 16)
ORANGE_D = (198, 120, 6)
GREY = (122, 116, 108)
LIGHT = (252, 246, 234)
GREEN = (72, 132, 96)
RED = (196, 72, 56)

FB = r"C:\Windows\Fonts\msyhbd.ttc"
FR = r"C:\Windows\Fonts\msyh.ttc"


def F(size, bold=True):
    try:
        return ImageFont.truetype(FB if bold else FR, size)
    except Exception:
        return ImageFont.load_default()


def halftone(size, step=7):
    ov = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(0, size[1], step):
        for x in range(0, size[0], step):
            d.ellipse([x, y, x + 2, y + 2], fill=(0, 0, 0, 24))
    return ov


def phone(x, y, w, h, r=40):
    d = ImageDraw.Draw(CANVAS)
    d.rounded_rectangle([x - 9, y - 9, x + w + 9, y + h + 9], radius=r + 9, fill=DARK)
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=LIGHT)
    d.rounded_rectangle([x + w // 2 - 66, y + 13, x + w // 2 + 66, y + 31],
                        radius=9, fill=DARK)


def status(d, x, y, w, t="15:20"):
    d.text((x + 32, y + 44), t, font=F(21), fill=DARK)
    bx = x + w - 38
    for i in range(4):
        hh = 6 + i * 4
        d.rectangle([bx - 74 + i * 9, y + 60 - hh, bx - 68 + i * 9, y + 60], fill=DARK)
    d.rounded_rectangle([bx - 32, y + 46, bx - 2, y + 60], radius=3, outline=DARK, width=2)
    d.rectangle([bx - 28, y + 50, bx - 13, y + 56], fill=DARK)


def center(d, cx, y, txt, font, fill=DARK):
    bb = d.textbbox((0, 0), txt, font=font)
    d.text((cx - (bb[2] - bb[0]) / 2, y), txt, font=font, fill=fill)


def wrap(d, txt, font, maxw):
    lines, cur = [], ""
    for ch in txt:
        if d.textlength(cur + ch, font=font) > maxw:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


# ─────────────────────────── 01 订单备注 ───────────────────────────
def shot_01():
    global CANVAS
    im = Image.new("RGB", (W, H), CREAM)
    CANVAS = im
    d = ImageDraw.Draw(im)
    d.ellipse([-200, 400, 500, 920], fill=(228, 210, 176))
    d.ellipse([880, -180, 1520, 400], fill=(232, 214, 180))

    pw, ph = 576, 600
    px, py = (W - pw) // 2, (H - ph) // 2 - 6
    phone(px, py, pw, ph)
    d = ImageDraw.Draw(im)
    status(d, px, py, pw, "15:20")

    cx = px + pw / 2
    d.text((px + 40, py + 88), "订单详情", font=F(25), fill=GREY)
    d.line([px + 40, py + 126, px + pw - 40, py + 126], fill=(214, 198, 166), width=2)

    # 备注卡片（黄色高亮，全片最重要的信息）
    # ⚠️ 不要用 ⚠/emoji —— 微软雅黑不含这些字形，会渲染成方框
    d.rounded_rectangle([px + 32, py + 146, px + pw - 32, py + 392],
                        radius=22, fill=(252, 232, 176), outline=ORANGE_D, width=4)
    d.text((px + 54, py + 166), "客户备注", font=F(23), fill=ORANGE_D)

    note = "千万别按门铃！我家鹦鹉会学，学会就停不下来。"
    lines = wrap(d, note, F(34), pw - 110)
    yy = py + 212
    for ln in lines:
        d.text((px + 54, yy), ln, font=F(34), fill=DARK)
        yy += 48

    # 底部：放门口
    d.rounded_rectangle([px + 32, py + 418, px + pw - 32, py + 480],
                        radius=16, fill=(238, 230, 212))
    d.text((px + 54, py + 432), "请放门口，无需敲门", font=F(23, False), fill=GREY)

    # 按钮
    d.rounded_rectangle([px + 32, py + 498, px + pw - 32, py + 566],
                        radius=26, fill=ORANGE, outline=DARK, width=4)
    center(d, cx, py + 518, "确认接单", F(34), DARK)

    return Image.alpha_composite(im.convert("RGBA"), halftone((W, H))).convert("RGB")


# ─────────────────────────── 15 静音模式 ───────────────────────────
def shot_15():
    global CANVAS
    im = Image.new("RGB", (W, H), CREAM)
    CANVAS = im
    d = ImageDraw.Draw(im)
    d.ellipse([-180, 380, 480, 900], fill=(228, 210, 176))

    pw, ph = 560, 596
    px, py = (W - pw) // 2, (H - ph) // 2 - 6
    phone(px, py, pw, ph)
    d = ImageDraw.Draw(im)
    status(d, px, py, pw, "15:31")

    cx, cy = px + pw / 2, py + 292

    # 静音图标：铃铛 + 斜线
    bx, by = cx, cy - 60
    d.pieslice([bx - 58, by - 58, bx + 58, by + 34], 180, 360, fill=LIGHT, outline=DARK, width=5)
    d.line([bx - 58, by - 12, bx - 58, by + 30], fill=DARK, width=5)
    d.line([bx + 58, by - 12, bx + 58, by + 30], fill=DARK, width=5)
    d.line([bx - 58, by + 30, bx + 58, by + 30], fill=DARK, width=5)
    d.ellipse([bx - 12, by + 28, bx + 12, by + 52], outline=DARK, width=5)

    # 斜线（静音）
    d.line([bx - 80, by - 76, bx + 80, by + 70], fill=RED, width=11)
    d.line([bx - 76, by - 70, bx + 76, by + 64], fill=RED, width=11)

    center(d, cx, cy + 70, "静 音", F(56), DARK)
    center(d, cx, cy + 142, "已开启", F(28, False), GREY)

    # 底部：小字说明
    d.rounded_rectangle([px + 46, py + 468, px + pw - 46, py + 536],
                        radius=18, fill=(238, 230, 212))
    center(d, cx, py + 484, "来电与通知将不会响铃", F(23, False), GREY)

    return Image.alpha_composite(im.convert("RGBA"), halftone((W, H))).convert("RGB")


# ─────────────────────────── 动画 ───────────────────────────
def anim(png, dst, seconds, mode):
    """轻微动效：推近 + 可选高亮脉冲，让静态 UI 不显死板"""
    base = Image.open(png).convert("RGB")
    bw, bh = base.size
    n = int(round(seconds * FPS))
    frames = bytearray()
    for i in range(n):
        t = i / max(1, n - 1)
        e = t * t * (3 - 2 * t)
        s = 1.0 + 0.05 * e
        cw, ch = W / s, H / s
        scale = max(W / bw, H / bh)
        b2 = base.resize((int(bw * scale), int(bh * scale)), Image.LANCZOS)
        cx, cy = b2.width / 2, b2.height / 2
        box = (int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))
        box = (max(0, box[0]), max(0, box[1]), min(b2.width, box[2]), min(b2.height, box[3]))
        crop = b2.crop(box).resize((W, H), Image.LANCZOS)
        arr = np.asarray(crop).astype(np.float32)
        if mode == "pulse" and 0.25 < t < 0.65:
            g = math.sin((t - 0.25) / 0.40 * math.pi) * 0.10
            arr = arr * (1 + g)
        frames += np.clip(arr, 0, 255).astype(np.uint8).tobytes()
    subprocess.run([FF, "-y", "-v", "error",
                    "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                    "-r", str(FPS), "-i", "-",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-an", dst],
                   input=bytes(frames), check=True)
    return dst


JOBS = [
    ("01_phone_note", shot_01, 6.0, "push"),
    ("15_silent", shot_15, 5.0, "pulse"),
]

if __name__ == "__main__":
    for name, fn, sec, mode in JOBS:
        png = os.path.join(EP, name + ".png")
        fn().save(png, "PNG", optimize=True)
        mp4 = os.path.join(OUT, name + ".mp4")
        anim(png, mp4, sec, mode)
        print(f"  ✓ {name}  {sec}s  {os.path.getsize(mp4)//1024} KB")
    print(f"\n→ {OUT}")
