#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
阿甘定妆 v2 —— 先攻"耳朵"这一个锚点

诊断（v1 三张全部失败）：
  · 三张全是【垂耳】——模型把"卡通驴"默认画成垂耳小狗
  · 左耳【完全没有缺角】
  · 圆肚子，不瘦小
  · 日系大眼萌，不是美式复古

策略（《走蛟》教训：**写视觉，不写定义**）：
  · 不写 hinny / donkey mule —— 模型不认这个生物学概念
  · 耳朵放到 prompt 最前面，用最强视觉词，且明确"向上、挺立、像天线"
  · 缺角单独强调，用"被咬掉一角"这种具体意象
  · 体型写"瘦骨嶙峋、扁肚子、细长腿"，不写 "slim"
  · 风格锚：美式复古，眼白多、脸长、线条硬

本轮只出【正面半身】，不碰三视图 ——
三视图会分散注意力，先把单个锚点定死再扩展。
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

STYLE = ("american retro cartoon style of the 1950s, thick wobbly black ink outlines, "
         "flat solid colors, visible halftone dot texture on shading, warm sepia palette, "
         "nostalgic storybook mood")

# ★ 耳朵放最前（权重最高），因为这是 v1 失败的唯一死因
EAR = ("HER TWO LONG EARS STAND STRAIGHT UP AND OUT FROM THE TOP OF HER HEAD, "
       "stiff, erect and pointed at the sky like two radio antennas, "
       "each ear a long tapered blade with a soft inner curve, "
       "clearly upright and never flopping down, "
       "the very tip of her LEFT ear has a small triangular piece missing — "
       "a clean chipped notch, easy to see in silhouette, ")

FACE = ("a long narrow donkey muzzle with a straight nose bridge and a soft grey-pink nose, "
        "large round eyes set wide apart with plenty of white and warm brown irises, "
        "a calm gentle half-smile, ")

BODY = ("a lean bony little body, flat hollow belly, thin long legs, narrow shoulders, "
        "short neck held level, a short flat mane lying down along the back of the neck only, "
        "skinny arms ending in three-fingered hoof-hands, small cloven hooves for feet, ")

BASE = EAR + FACE + BODY + "dusty sorrel brown coat with a lighter muzzle, "

VARIANTS = [
    ("V1", "head and shoulders portrait, front view, looking at the viewer, "
           "plain warm cream background, " + BASE + STYLE),

    # V2：强调"缺角在剪影里能看见"，并加一个更硬的角度词
    ("V2", "head and shoulders portrait, front view, head tilted slightly, "
           "plain warm cream background, " + BASE +
           "the chipped notch of the left ear breaks the outer outline clearly, " + STYLE),

    # V3：把"驴脸"说得更具体（长脸 + 直鼻梁），去掉可爱感
    ("V3", "head and shoulders portrait, three-quarter front view, "
           "a long-faced pack animal with a plain hard-working expression, "
           "slightly tired eyes, plain warm cream background, " + BASE + STYLE),

    # V4：正面全身，验证体型是否够瘦
    ("V4", "full body standing portrait, front view, slightly leaning forward as if "
           "always in a hurry, plain warm cream background, " + BASE + STYLE),
]

if __name__ == "__main__":
    ok = 0
    for tag, prompt in VARIANTS:
        out = os.path.join(BATCH, f"AGAN_{tag}.png")
        try:
            t0 = time.time()
            paths = agnes.gen_image(prompt, size="2K", ratio="3:4", save_to=out)
            dt = time.time() - t0
            for p in paths:
                with open(os.path.splitext(p)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
                    f.write(json.dumps({"tag": tag, "prompt": prompt, "negative": None,
                                        "size": "2K", "ratio": "3:4",
                                        "model": agnes.IMG_MODEL,
                                        "elapsed_s": round(dt, 1)}, ensure_ascii=False, indent=2))
                print(f"  ✓ {os.path.basename(p)}  {dt:.0f}s")
                ok += 1
        except Exception as e:
            print(f"  ✗ {tag}: {str(e)[:160]}")
    print(f"\n共 {ok} 张 → {BATCH}")
