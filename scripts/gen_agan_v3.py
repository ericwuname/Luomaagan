#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
阿甘定妆 v3 —— 修"漂移成纯驴"

v2 复盘：
  ✅ 耳朵立起来了（关键突破）
  ❌ 但立刻变纯驴：长矛耳 + 直立鬃 + 灰毛 + 白唇（交接书明令禁止的四条）
  ❌ 左耳缺角 4 张全失败
  ❌ V4 身体和头颜色不一致

根因分析（关键洞察）：
  模型只知道"驴 = 长矛耳 + 直立鬃 + 灰毛"，"马 = 短耳 + 倒伏鬃 + 骝色"。
  **它不理解"中间态"。** 所以一叫"立耳"就往驴跑。

破解思路：
  骡子 = 马的体型 + 驴的脸。**那就用"马"讲身体和毛色，用"驴"只讲脸。**
  · 耳朵：不写 long tapered blade（那会引导成矛），改 medium-length + rounded tip
  · 鬃毛：必须写"倒伏、偏向一侧"（马的鬃），这是最有效的反驴锚点
  · 毛色：不写 dusty（会变灰），写 reddish-chestnut / sorrel
  · 白唇：不写（负面词无效，只能靠正向覆盖）→ 写 "muzzle the same warm brown, only slightly lighter"

缺角方案：
  v2 用 "small triangular piece missing" 4 张全失败。
  本轮 A 方案继续试缺角，B 方案换成【左耳折角】——折角在剪影里更明显，
  也更像"干了一辈子活"的记号（参考拳击手的耳朵）。
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
         "visible halftone dot texture, warm sepia palette, nostalgic storybook mood")

# ★ 反驴三件套：身体、鬃毛、毛色 —— 全用"马"的语言
BODY_HORSE = ("the body of a young workhorse, lean and wiry with long slim legs and a flat belly, "
              "narrow chest and narrow shoulders, short straight neck, ")

MANE_HORSE = ("a cropped mane that grows only in a short narrow strip along the ridge of the neck "
              "and falls over flat to one side, lying down against the skin, ")

COAT_HORSE = ("a warm reddish-chestnut coat, glossy sorrel brown, "
              "only the muzzle is a shade lighter, the lips stay the same warm brown as the face, ")

# ★ 耳朵：立着，但是圆头的"叶片"，不是矛尖
EAR_BASE = ("two medium-length ears standing upright and slightly outward from the top of the head, "
            "each shaped like a rounded leaf with a soft blunt tip, "
            "stiff and erect, held up like a pair of antennas, ")

EAR_CHIP = EAR_BASE + ("the tip of the LEFT ear has a small piece broken off, "
                       "a clear angular missing corner that dents the outline, ")

EAR_FOLD = EAR_BASE + ("the LEFT ear has a permanent fold near its tip, "
                       "the top third bent over and drooping slightly like a boxer's ear, "
                       "which breaks the outline of that ear, ")

FACE = ("a long straight profile like a donkey's face, plain and hardworking, "
        "large round eyes with plenty of white and warm brown irises, "
        "a calm closed-mouth smile, ")

HANDS = ("arms ending in three-fingered hoof-hands, small cloven hooves for feet, barefoot, ")

VARIANTS = [
    ("X1", "head and shoulders portrait, front view, plain warm cream background, "
           + EAR_CHIP + FACE + MANE_HORSE + COAT_HORSE + STYLE),

    ("X2", "head and shoulders portrait, front view, plain warm cream background, "
           + EAR_FOLD + FACE + MANE_HORSE + COAT_HORSE + STYLE),

    ("X3", "full body standing portrait, front view, leaning slightly forward as if always hurrying, "
           "plain warm cream background, "
           + EAR_CHIP + FACE + BODY_HORSE + MANE_HORSE + HANDS + COAT_HORSE + STYLE),

    ("X4", "full body standing portrait, front view, leaning slightly forward, "
           "plain warm cream background, "
           + EAR_FOLD + FACE + BODY_HORSE + MANE_HORSE + HANDS + COAT_HORSE + STYLE),
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
                    f.write(json.dumps({"tag": tag, "prompt": prompt,
                                        "size": "2K", "ratio": "3:4",
                                        "model": agnes.IMG_MODEL,
                                        "elapsed_s": round(dt, 1)}, ensure_ascii=False, indent=2))
                print(f"  ✓ {os.path.basename(p)}  {dt:.0f}s")
                ok += 1
        except Exception as e:
            print(f"  ✗ {tag}: {str(e)[:160]}")
    print(f"\n共 {ok} 张 → {BATCH}")
