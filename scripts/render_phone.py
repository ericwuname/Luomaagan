#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
手机屏幕镜头 —— 程序化渲染（不用 AI）

⛔ 为什么必须程序画
   这 4 个镜头承担全片最关键的信息交代：
     S01「已完成 9996 单」  → 观众立刻知道他是骑手、第一万单在即
     S04「第 9997 单」      → 仪式感开始
     S20「第 9999 单 完成」 → 只差一单
     S22「第 10000 单」     → 里程碑
   **AI 生成中文必然乱码**，这四镜一旦糊掉，观众就不知道他在干什么了。

✅ 做法
   用 PIL 画一个外卖 App 界面，中文用微软雅黑（msyhbd.ttc），
   数字用超大字号强调。风格跟片子统一：暖米底 + 粗黑描边 + 网点。
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01c")
os.makedirs(EP, exist_ok=True)

W, H = 1280, 704

CREAM = (240, 224, 192)
DARK = (26, 20, 16)
ORANGE = (240, 160, 16)
ORANGE_D = (200, 122, 6)
GREY = (120, 116, 108)
LIGHT = (252, 246, 232)
GREEN = (72, 132, 96)

FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_R = r"C:\Windows\Fonts\msyh.ttc"


def F(size, bold=True):
    try:
        return ImageFont.truetype(FONT_B if bold else FONT_R, size)
    except Exception:
        return ImageFont.load_default()


def halftone(size, step=7, dot=(0, 0, 0, 26)):
    """网点质感（和片子风格统一）"""
    w, h = size
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(0, h, step):
        for x in range(0, w, step):
            d.ellipse([x, y, x + 2, y + 2], fill=dot)
    return ov


def phone_frame(canvas, x, y, w, h, r=42):
    """画手机外壳 + 屏幕区"""
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([x - 10, y - 10, x + w + 10, y + h + 10], radius=r + 10,
                        fill=DARK)
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=LIGHT)
    # 刘海
    d.rounded_rectangle([x + w // 2 - 70, y + 14, x + w // 2 + 70, y + 34],
                        radius=10, fill=DARK)
    return x, y, w, h


def status_bar(d, x, y, w, time_txt="9:41"):
    d.text((x + 34, y + 46), time_txt, font=F(22), fill=DARK)
    # 信号 / 电量
    bx = x + w - 40
    for i in range(4):
        hh = 6 + i * 4
        d.rectangle([bx - 76 + i * 9, y + 62 - hh, bx - 70 + i * 9, y + 62], fill=DARK)
    d.rounded_rectangle([bx - 34, y + 48, bx - 2, y + 62], radius=3,
                        outline=DARK, width=2)
    d.rectangle([bx - 30, y + 52, bx - 14, y + 58], fill=DARK)


def card(d, x, y, w, h, fill=CREAM, outline=DARK, width=4, r=26):
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill,
                        outline=outline, width=width)


def center(d, cx, y, text, font, fill=DARK):
    bb = d.textbbox((0, 0), text, font=font)
    d.text((cx - (bb[2] - bb[0]) / 2, y), text, font=font, fill=fill)


def shot_s01():
    """今日已送达 9996 单"""
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    # 桌面背景虚化块
    d.ellipse([-200, 420, 480, 900], fill=(228, 210, 176))
    d.ellipse([900, -160, 1500, 380], fill=(232, 214, 180))

    pw, ph = 620, 600
    px, py = (W - pw) // 2, (H - ph) // 2 - 10
    phone_frame(im, px, py, pw, ph)
    d = ImageDraw.Draw(im)
    status_bar(d, px, py, pw, "9:41")

    cx = px + pw / 2
    d.text((px + 44, py + 100), "今日已送达", font=F(28), fill=GREY)

    # 超大数字
    center(d, cx, py + 158, "9996", F(168), DARK)
    center(d, cx, py + 360, "单", F(40), GREY)

    card(d, px + 40, py + 428, pw - 80, 110, ORANGE, DARK, 4, 30)
    center(d, cx, py + 458, "继续接单", F(40), DARK)

    im = Image.alpha_composite(im.convert("RGBA"), halftone((W, H)))
    return im.convert("RGB")


def shot_s04():
    """新订单：第 9997 单"""
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    d.ellipse([820, 380, 1500, 900], fill=(228, 210, 176))

    pw, ph = 620, 600
    px, py = (W - pw) // 2, (H - ph) // 2 - 10
    phone_frame(im, px, py, pw, ph)
    d = ImageDraw.Draw(im)
    status_bar(d, px, py, pw, "9:47")

    cx = px + pw / 2
    # 弹窗标题
    center(d, cx, py + 96, "新 订 单", F(34), GREY)

    # 单号（仪式感）
    center(d, cx, py + 146, "第 9997 单", F(64), ORANGE_D)

    card(d, px + 40, py + 246, pw - 80, 190, LIGHT, DARK, 3, 24)
    d = ImageDraw.Draw(im)
    d.text((px + 68, py + 272), "柳树巷 3 号 · 奶茶 1 杯", font=F(26, False), fill=DARK)
    d.text((px + 68, py + 314), "距您 800 米", font=F(24, False), fill=GREY)
    d.text((px + 68, py + 352), "预计 8 分钟送达", font=F(24, False), fill=GREY)

    card(d, px + 40, py + 456, pw - 80, 104, ORANGE, DARK, 4, 28)
    center(d, cx, py + 482, "接单", F(42), DARK)

    im = Image.alpha_composite(im.convert("RGBA"), halftone((W, H)))
    return im.convert("RGB")


def shot_s20():
    """第 9999 单 已完成"""
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    d.ellipse([-180, -140, 420, 400], fill=(228, 210, 176))

    pw, ph = 620, 600
    px, py = (W - pw) // 2, (H - ph) // 2 - 10
    phone_frame(im, px, py, pw, ph)
    d = ImageDraw.Draw(im)
    status_bar(d, px, py, pw, "18:52")

    cx = px + pw / 2
    # 对勾
    d.ellipse([cx - 42, py + 88, cx + 42, py + 172], outline=GREEN, width=8)
    d.line([cx - 20, py + 130, cx - 4, py + 148], fill=GREEN, width=9)
    d.line([cx - 4, py + 148, cx + 24, py + 112], fill=GREEN, width=9)

    center(d, cx, py + 196, "已送达", F(38), GREY)
    center(d, cx, py + 252, "第 9999 单", F(72), DARK)

    d.text((px + 48, py + 386), "客户评价", font=F(26, False), fill=GREY)
    # 五星
    for i in range(5):
        sx = px + 52 + i * 44
        sy = py + 428
        pts = []
        import math
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            rr = 17 if k % 2 == 0 else 7
            pts.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
        d.polygon(pts, fill=ORANGE, outline=DARK)

    # 底部提示
    card(d, px + 40, py + 486, pw - 80, 84, CREAM, DARK, 3, 24)
    center(d, cx, py + 506, "还差 1 单", F(32), ORANGE_D)

    im = Image.alpha_composite(im.convert("RGBA"), halftone((W, H)))
    return im.convert("RGB")


def shot_s22():
    """第 10000 单"""
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    # 夜色底
    d.rectangle([0, 0, W, H], fill=(236, 218, 184))
    d.ellipse([-220, 320, 520, 980], fill=(224, 204, 168))
    d.ellipse([860, -200, 1560, 420], fill=(230, 212, 176))

    pw, ph = 620, 600
    px, py = (W - pw) // 2, (H - ph) // 2 - 10
    phone_frame(im, px, py, pw, ph)
    d = ImageDraw.Draw(im)
    status_bar(d, px, py, pw, "19:40")

    cx = px + pw / 2
    center(d, cx, py + 88, "新 订 单", F(34), GREY)

    # ★ 10000 巨大
    center(d, cx, py + 132, "第 10000 单", F(84), ORANGE_D)

    card(d, px + 40, py + 262, pw - 80, 176, LIGHT, DARK, 3, 24)
    d = ImageDraw.Draw(im)
    d.text((px + 68, py + 288), "柳树巷 7 号 · 外卖 1 份", font=F(25, False), fill=DARK)
    d.text((px + 68, py + 330), "距您 1.2 公里", font=F(24, False), fill=GREY)
    # ⚠️ 原写"这一单，等很久了"——是伏笔但剧本里没回收，会误导观众。
    #    改成中性信息，不埋不回收的钩子。
    d.text((px + 68, py + 366), "预计 12 分钟送达", font=F(24, False), fill=GREY)

    card(d, px + 40, py + 458, pw - 80, 104, ORANGE, DARK, 4, 28)
    center(d, cx, py + 484, "接单", F(42), DARK)

    im = Image.alpha_composite(im.convert("RGBA"), halftone((W, H)))
    return im.convert("RGB")


SHOTS = {"S01_phone": shot_s01, "S04_phone": shot_s04,
         "S20_phone": shot_s20, "S22_phone": shot_s22}

if __name__ == "__main__":
    for name, fn in SHOTS.items():
        out = os.path.join(EP, name + ".png")
        fn().save(out, "PNG", optimize=True)
        print(f"  ✓ {name}  {os.path.getsize(out)//1024} KB")
    print(f"\n→ {EP}")
