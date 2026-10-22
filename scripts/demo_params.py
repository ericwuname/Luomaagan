#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
参数演示 —— 证明「改一个数字，立刻看到效果」

同一个骨架，只改几个参数，出四张完全不同的角色。
这是参数化相对 AI 生成的核心差异：
  AI：说"耳朵短一点" → 整张重画，脸、姿态全变（概率）
  这里：改 ear_len=0.8 → 只有耳朵变，其他一模一样（确定）
"""
import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("agan", os.path.join(HERE, "agan_svg.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

OUT = os.path.join(os.path.dirname(HERE), "work", "char", "svg")
os.makedirs(OUT, exist_ok=True)

VARIANTS = {
    "A_基准": {},
    "B_长脸驴味": dict(face_len=0.85, ear_len=1.35, neck_len=0.85),
    "C_大头萌": dict(head_r=1.62, face_len=0.22, hand_r=1.3),
    "D_修长瘦高": dict(leg_len=1.25, body_h=1.05, body_w=0.86, head_r=1.15),
    "E_小头壮实": dict(head_r=1.05, body_w=1.30, body_h=0.72, arm_w=2.1),
    "F_不戴帽": dict(show_cap=False, show_bag=False),
}

if __name__ == "__main__":
    import cairosvg
    for name, kw in VARIANTS.items():
        a = m.Agan(**kw)
        s = a.svg()
        base = os.path.join(OUT, f"PARAM_{name}")
        with open(base + ".svg", "w", encoding="utf-8") as f:
            f.write(s)
        cairosvg.svg2png(bytestring=s.encode("utf-8"), write_to=base + ".png",
                         output_width=a.p["W"], output_height=a.p["H"])
        print(f"  ✓ {name}")

    # 拼对比图
    from PIL import Image, ImageDraw
    files = [os.path.join(OUT, f"PARAM_{k}.png") for k in VARIANTS]
    ims = [(k, Image.open(f).convert("RGB")) for k, f in zip(VARIANTS, files)]
    cols = 3
    tw, th = 320, 480
    for name, im in ims:
        im.thumbnail((tw, th), Image.LANCZOS)
    rows = (len(ims) + cols - 1) // cols
    W = cols * (tw + 14) + 14
    H = rows * (th + 40) + 14
    sheet = Image.new("RGB", (W, H), (238, 236, 230))
    d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(ims):
        r, c = divmod(i, cols)
        x = 14 + c * (tw + 14)
        y = 14 + r * (th + 40)
        d.text((x + 4, y), name, fill=(20, 20, 20))
        sheet.paste(im, (x + (tw - im.size[0]) // 2, y + 20))
    out = os.path.join(OUT, "PARAM_对比.png")
    sheet.save(out)
    print(f"✓ {out}")
