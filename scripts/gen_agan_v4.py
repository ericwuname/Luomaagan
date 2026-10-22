#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
阿甘定妆 v4 —— 按【形状语言】重做，四个大胆方案

诊断（用户：主角没有一眼记住的特征）：
  v1~v3 共 11 张，全部是【全身圆形语言】——圆身、圆脸、圆眼。
  **圆形 = 温暖友好天真 = 可爱，但"可爱"正是没有记忆点的原因。**
  海绵宝宝能记住是因为他是【方形】，米老鼠是【三个圆的构成】，
  哆啦A梦是【圆 + 一个红鼻子的强色点】——都靠"形状本身就是记忆点"。

查证到的四条硬规律：
  1. 迪士尼「10 英里剪影测试」：纯黑形状就要能读懂
  2. 形状语言：圆=温暖/方=固执扎实/三角=危险锐利
  3. **"主形稳定，副形捣乱"**——全身是圆会失去张力，要有一处冲突
  4. 比例是语法：3-4头身=想保护它 / 4-5=滑稽亲切 / 6=风格化
  5. 每角色限制 3-5 种主导色，要有「固有识别色」

阿甘的性格：乐观、倔强、底层但不阴暗，"知道生活很难但选择笑着扛"
  → **倔强 = 方形**。这才是他的主形，不是圆形。

四个方案（都在解决"形状即记忆点"）：
  P1 方箱骡    —— 身体是一个方盒子（外卖箱长在身上，像龟壳）+ 长驴脸 + 四根细腿
  P2 长脸天线  —— 脸占全身 1/2，耳朵像两片雷达天线，身体瘦成一条
  P3 弹簧脖    —— 脖子细长永远前倾 30°，头大身小，像一根被压弯的弹簧
  P4 旧玩具    —— 用了很久的旧毛绒：补丁、掉毛、一只耳立一只耳塌

每方案出 2 张（正面 + 全身），共 8 张。
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

# 反驴漂移三件套（v3 验证有效）
HORSE = ("reddish-chestnut coat, glossy sorrel brown, "
         "a short mane in one narrow strip that lies flat and falls to one side, ")

SCHEMES = {
 # ── P1：方箱骡 —— 最强方案，把"职业"和"形状"和"记忆点"三合一 ──
 "P1a": (
   "front view character design, plain warm cream background, "
   "THIS IS THE KEY: **his torso is a solid BOX SHAPE** — a squarish, slightly "
   "tapered rectangular body with flat front panel and softly rounded corners, "
   "like a living delivery crate that grew on him, "
   "a small square head sitting directly on top of the box with almost no neck, "
   "a long narrow donkey face on that square head, "
   "two long ears standing straight up, "
   "four very thin stick-like legs coming out of the bottom of the box, tiny hooves, "
   "square body, long face, thin stick legs — extreme contrast, "
   + HORSE + STYLE),

 "P1b": (
   "full body character design, front view, plain warm cream background, "
   "**a BOX-SHAPED body**: a chunky squarish torso with a flat front like a wooden "
   "crate, rounded corners, visibly wider than tall, "
   "a small square head on top with a long narrow donkey muzzle, "
   "two upright ears, four thin spindly legs, tiny hooves, "
   "one arm holding a delivery bag overhead, "
   + HORSE + STYLE),

 # ── P2：长脸天线 —— 把"驴脸"极端化 ──
 "P2a": (
   "front view character design, plain warm cream background, "
   "**an extremely LONG face**: the head is a tall narrow rectangle, "
   "the muzzle alone is half the total head height, making the face read as a long "
   "vertical slab, "
   "two huge ears shaped like radar antennas standing up and slightly out, "
   "a small skinny body underneath, four thin legs, "
   "face is the dominant shape of the whole character, "
   + HORSE + STYLE),

 "P2b": (
   "full body front view, plain warm cream background, "
   "**the body is a thin vertical strip** and the head is a tall narrow slab, "
   "so the whole silhouette reads like a tall rectangle standing on thin legs, "
   "a very long donkey face taking most of the head, two big upright antenna ears, "
   + HORSE + STYLE),

 # ── P3：弹簧脖 —— 把"倔"视觉化 ──
 "P3a": (
   "front view character design, plain warm cream background, "
   "**a long thin neck permanently bent forward at a 30 degree angle**, "
   "as if he is forever leaning into a headwind and refusing to stop, "
   "big head with a long donkey face at the end of that bent neck, "
   "two upright ears, a small compact body, thin legs, "
   "the bent neck is the dominant shape of the silhouette, "
   + HORSE + STYLE),

 "P3b": (
   "full body front view, plain warm cream background, "
   "**a bent neck arc** that starts at the shoulders and curves forward like a "
   "question mark, head hanging at the front of that arc, "
   "small lean body, four thin legs planted wide, "
   + HORSE + STYLE),

 # ── P4：旧玩具 —— 用"破损"当记忆点 ──
 "P4a": (
   "front view character design, plain warm cream background, "
   "**an old worn-out plush toy that has been used for years**: "
   "patched stitches on the cheek, one seam repaired with visible thread, "
   "slightly uneven eyes, one ear standing up and the other one folded down, "
   "faded sun-bleached coat with lighter worn areas on the knees, "
   "a long donkey face, thin legs, "
   + HORSE + STYLE),

 "P4b": (
   "full body front view, plain warm cream background, "
   "**a much-loved battered toy**: visible patches, one ear up and one ear flopped over, "
   "a small tear repaired with cross stitching on the shoulder, "
   "faded coat, four thin legs, long donkey face, "
   + HORSE + STYLE),
}

if __name__ == "__main__":
    ok = 0
    for tag, prompt in SCHEMES.items():
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
