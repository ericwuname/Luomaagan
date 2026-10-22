#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
阿甘角色 v10 —— 综合 Claude 的 D1（表情）+ D2（毛色）

用户给的 Claude D 方案（单变量对比）：
  D0 原版：栗褐毛色，窄长耳朵，抿嘴微笑
  D1 改表情：张嘴大笑，两颗大门牙，眉毛抬高，眼睛更大
  D2 改毛色：灰蓝毛色，粉色耳内，配橙黄衣更跳
  D3 改耳朵：耳朵更宽更圆，更像驴耳，不那么像兔子

用户要求："参考 D2、D1，综合一下"

⚠️ 一个必须说明的冲突：
   交接书明确写"毛色避免纯驴灰"。
   D2 的灰蓝严格说不是"驴灰"（偏蓝、带饱和度），而且配橙黄衣对比强、辨识度高，
   但它确实更冷——和"暖褐色调、治愈"的调性有张力。
   所以本批把 D2 毛色和 D1 表情拆开组合，让实际效果说话。

四张组合：
  E1 = D2 毛色 + 原表情（抿嘴笑）
  E2 = D2 毛色 + D1 表情（张嘴大笑、门牙、眉毛抬高）
  E3 = 栗棕毛色 + D1 表情（保守方案：保留暖调，只要表情）
  E4 = D2 毛色 + D1 表情 + D3 宽圆耳（全采纳）
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATCH = os.path.join(ROOT, "work", "char", time.strftime("batch_%Y%m%d_%H%M"))
os.makedirs(BATCH, exist_ok=True)

STYLE = ("american retro cartoon style, thick wobbly black ink outlines, flat solid colors, "
         "visible halftone dot texture, warm cream background, "
         "clean simple shapes like a vintage storybook character sheet")

BASE = ("full body character design, front view, standing upright on two legs, "
        "a small anthropomorphic hinny delivery rider, "
        "**a horse's compact body with a donkey's long straight face**, "
        "lean and wiry, thin legs, small cloven hooves, "
        "an oversized round head sitting on a short neck, "
        "**very large round eyes with big white sclera and clear catchlights**, "
        "**wearing a mustard-yellow sleeveless uniform vest and a small orange delivery satchel "
        "on his back**, "
        "a short flat mane, a thin tail with a tuft at the tip, ")

# ── 表情两版 ──
SMILE = ("a gentle closed-mouth smile, calm kind expression, ")
LAUGH = ("**a wide open-mouthed laugh showing two big front teeth**, "
         "**eyebrows raised high**, eyes even bigger and brighter, "
         "an ecstatic goofy happy expression, ")

# ── 毛色两版 ──
COAT_MULE = ("chestnut-brown coat with a lighter cream muzzle, ")
COAT_D2 = ("**a soft dusty slate-blue-grey coat with a pale cream muzzle**, "
           "**big pink inner ears**, the blue-grey fur contrasts strongly with the "
           "mustard-yellow vest, ")

# ── 耳朵两版 ──
EAR_NARROW = ("two long narrow upright ears, each a slim tapered leaf, ")
EAR_D3 = ("**two wide rounded donkey ears**, broader and rounder than a rabbit's, "
          "with soft curved outer edges, ")

VARIANTS = {
 "E1": BASE + COAT_D2 + EAR_NARROW + SMILE + STYLE,
 "E2": BASE + COAT_D2 + EAR_NARROW + LAUGH + STYLE,
 "E3": BASE + COAT_MULE + EAR_NARROW + LAUGH + STYLE,
 "E4": BASE + COAT_D2 + EAR_D3 + LAUGH + STYLE,
}

if __name__ == "__main__":
    for tag, prompt in VARIANTS.items():
        out = os.path.join(BATCH, f"AGAN_{tag}.png")
        try:
            t0 = time.time()
            agnes.gen_image(prompt, size="2K", ratio="3:4", save_to=out)
            dt = time.time() - t0
            with open(os.path.splitext(out)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
                json.dump({"tag": tag, "prompt": prompt, "size": "2K",
                           "ratio": "3:4", "elapsed_s": round(dt, 1)},
                          f, ensure_ascii=False, indent=2)
            print(f"  ✓ {tag}  {dt:.0f}s")
        except Exception as e:
            print(f"  ✗ {tag}: {str(e)[:160]}")
    print(f"\n→ {BATCH}")
