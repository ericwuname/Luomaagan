#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
阿甘定妆 v5 —— 三源合体

v4 复盘（8 张，四个形状方案）：
  P1「方箱骡」  → ✅ **剪影最强**（方盒+驴头+细腿，一眼记住）
                    ❌ 拟人化不足，头从箱子正面钻出来，关系怪
  P2「长脸天线」→ ❌ 模型没理解"长脸"，画成大耳狐
  P3「弹簧脖」  → ❌ 模型没理解"弯脖"，画成普通驴
  P4「旧玩具」  → ✅ **拟人化最好**（两足站立、有手）+ 补丁缝线的破损质感很打动人
                    ❌ 变成布偶熊，失去驴骡物种感

合成方案（三个来源各取所长）：
  · 形状记忆点 ← P1 的方形躯干
  · 拟人化 + 破损 ← P4 的两足站立 + 补丁磨损
  · 物种正确 ← v3 的骝色 / 倒伏鬃 / 长驴脸

新增一条（查证）：**角色必须有「固有识别色」**——
  观众远距离也能认出的核心色。阿甘的识别色 = **黄袋鼠的亮黄**。
  → 躯干做成亮黄方箱，棕色骡子 + 黄色箱体，两色强对比。

四张：
  Q1 棕方箱躯干（低饱和，看形状）
  Q2 亮黄方箱躯干（看识别色）
  Q3 亮黄方箱 + 补丁磨损（看质感）
  Q4 亮黄方箱 + 左耳折角 + 标志动作举箱（看完整形态）
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

# 骡子的物种锚（v3 验证有效：用马讲身体，用驴讲脸）
MULE = ("his head is a long narrow donkey face with a straight profile, "
        "two long ears standing upright, "
        "a short mane in one narrow strip lying flat along the back of the neck, "
        "the face and limbs are warm reddish-chestnut brown, glossy sorrel")

# ★ 核心形状：方形躯干 + 拟人站立
BOX = ("**he stands upright on two legs like a person**, "
       "**his torso is one solid SQUARE BOX shape** — a squarish chunky body with a "
       "flat front panel and softly rounded corners, wider than it is tall, "
       "like a living parcel crate that grew onto him, "
       "two skinny arms come out of the upper corners of the box, "
       "two thin spindly legs come out of the bottom of the box, small cloven hooves, ")

WEAR = ("his body is a bit worn: a patched seam stitched across one corner, "
        "faded scuffed paint at the edges, a small dent, ")

ARMS = "arms end in three-fingered hoof-hands, "

VARIANTS = {
 "Q1": "front view character design, plain warm cream background, "
       + BOX + MULE + ARMS + "the box torso is the same reddish-brown as his skin, "
       "no clothing, " + STYLE,

 "Q2": "front view character design, plain warm cream background, "
       + BOX + MULE + ARMS +
       "**the box torso is bright warm mustard yellow**, a strong solid yellow panel "
       "with a black outline, clearly different from his brown fur, "
       "no clothing, " + STYLE,

 "Q3": "front view character design, plain warm cream background, "
       + BOX + MULE + ARMS + WEAR +
       "**the box torso is bright warm mustard yellow**, a strong solid yellow panel, "
       "no clothing, " + STYLE,

 "Q4": "full body character design, front view, plain warm cream background, "
       + BOX + MULE + ARMS + WEAR +
       "**the box torso is bright warm mustard yellow**, "
       "**the tip of his LEFT ear is folded over and bent down**, "
       "he is holding a small delivery bag high above his head with one hand, "
       "leaning slightly forward as if always in a hurry, "
       "no clothing, " + STYLE,
}

if __name__ == "__main__":
    ok = 0
    for tag, prompt in VARIANTS.items():
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
