#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
重做 05 门铃 —— 第一版失败，换个思路

⛔ 第一版失败原因
   prompt 要求"蹄手停在按钮前一厘米，绝不触碰"。
   **结果：模型直接画成手指按在按钮上。**
   一厘米是极精细的空间控制，图像模型做不到；
   而且它天然倾向"手靠近按钮 = 手按按钮"这个语义。

✅ 第二版思路：**用构图代替距离**
   不在同一个局部区域放"手 + 按钮"，而是：
   · 门铃在画面左上
   · 蹄子在画面右下，**举在半空**
   · 两者之间是一大片空白
   这样"没碰到"是**构图保证**的，不依赖模型理解"一厘米"。

   另外：蹄子必须是**蹄**（分瓣、黑色），不是人手。
   第一版画成了人类手指，这在动物拟人世界里是硬伤。
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep02")
AGAN = os.path.join(ROOT, "assets", "hero", "AGAN_MASTER_2k.png")

STYLE = ("vintage American cartoon style, thick bold black ink outlines, "
         "flat solid colors, visible halftone dot texture, "
         "warm nostalgic picture-book mood, cinematic 16:9 composition")

VARIANTS = {
 # A：门铃左上 / 蹄子右下，中间大片空白
 "05_bell_A": (
   "**wide close-up of an apartment door, composed in two corners.** "
   "**In the UPPER LEFT of frame: a round dark doorbell button mounted on the door frame, "
   "unlit.** "
   "**In the LOWER RIGHT of frame: a slim grey donkey's hoof, with a black cloven tip, "
   "held up in mid-air, pointing toward the bell but nowhere near it.** "
   "**The middle of the frame between the hoof and the button is completely empty air — "
   "a large clear gap, they are far apart.** "
   "The hoof is a hoof, not a human hand. Shallow depth of field, warm corridor light, " + STYLE),

 # B：门铃在墙 / 蹄子在身侧垂着（更保守）
 "05_bell_B": (
   "**medium close-up from the side: an apartment doorway with a round dark doorbell button "
   "on the frame, unlit.** "
   "**A small slate blue-grey hinny stands in the corridor beside the door, his amber vest "
   "visible, and BOTH of his hooves are hanging down at his sides, clearly away from the "
   "door — his hooves are nowhere near the door.** "
   "**He is looking at the button without reaching for it, hesitating.** "
   "Slim black cloven hooves, not human hands. Warm corridor light, " + STYLE),
}

if __name__ == "__main__":
    for name, prompt in VARIANTS.items():
        out = os.path.join(EP, name + ".png")
        if os.path.exists(out) and os.path.getsize(out) > 200000:
            print(f"  · {name} 已存在")
            continue
        print(f"  → {name} ...", flush=True)
        try:
            t0 = time.time()
            agnes.gen_image(prompt, size="2K", ratio="16:9",
                            init_images=[AGAN], save_to=out)
            dt = time.time() - t0
            with open(os.path.splitext(out)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
                json.dump({"prompt": prompt, "elapsed_s": round(dt, 1)},
                          f, ensure_ascii=False, indent=2)
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
        except Exception as e:
            print(f"    ✗ {str(e)[:150]}", flush=True)
