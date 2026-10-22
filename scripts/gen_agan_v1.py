#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
阿甘定妆图 —— 第一批候选（裸角色三视图）

交接书 6.1 给了提示词。本脚本做两件事：
  1. 按交接书原样（含负面词）出一组
  2. 纯正向写法（不带负面词）出一组
     ← 《走蛟》教训：**负面词对具体部位会反向召唤**
       这里要验一下物种级负面词（pure donkey / horse body）是否也有这个问题
  3. 每张图旁存提示词原文与参数（交接书硬性要求：便于回溯）

产物：work/char/batch_<时间>/
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

STYLE = ("retro american cartoon style, thick wobbly black outlines, flat solid colors, "
         "halftone dot texture, warm sepia tone, nostalgic atmosphere")

# ── 核心造型（两份共用）──────────────────────────────
CORE = ("character design sheet, three views (front view / side view / three-quarter view) "
        "standing side by side, anthropomorphic donkey mule hinny, "
        "small slim body, short neck, slightly forward-leaning stance like always hurrying, "
        "medium-long ears shorter than a donkey's, LEFT ear tip has a chipped notch, "
        "short laid-back mane only along the back of the neck, "
        "short tail with bare upper half and a small tuft at the tip, "
        "hoof-like hands with three fingers, cloven hooves for feet, barefoot, "
        "coat color dusty sorrel brown, large friendly eyes, "
        "warm cream background, no clothes, no helmet, no text, no logo")

# A 组：交接书原样（带负面词）
A_PROMPT = CORE + ", " + STYLE
A_NEG = ("pure donkey, long spear ears, upright mane, gray donkey coat, white donkey lips, "
         "horse body, big muscular build, human hands, human feet, shoes, clothes, helmet, "
         "watermark, text, logo")

# B 组：纯正向（把 A 组的负面意思改写成正向肯定句，不用负面词）
B_PROMPT = (
    "character design sheet, three views (front view / side view / three-quarter view) "
    "standing side by side, anthropomorphic hinny — the offspring of a horse father and a "
    "donkey mother — a compact little pack animal that is bigger than a donkey and smaller "
    "than a horse, "
    "slim narrow build with thin legs, short neck, "
    "shoulders tilted forward as if permanently in a hurry, "
    "ears of medium length: longer than a horse's, clearly shorter than a donkey's, "
    "the left ear has a small missing notch at its tip, "
    "a short flat mane lying down along the back of the neck only, "
    "a short thin tail whose upper half is bare skin and whose tip carries one small tuft, "
    "hands shaped like soft hooves with three stubby fingers, "
    "feet are small cloven hooves, standing barefoot, "
    "coat is dusty sorrel brown with a slightly lighter muzzle, "
    "large warm friendly eyes with clear catchlights, "
    "warm cream background, bare body with no clothing and no helmet, "
    "clean image with no lettering and no emblem, " + STYLE
)

GROUPS = [("A", A_PROMPT, A_NEG, 3), ("B", B_PROMPT, None, 3)]

if __name__ == "__main__":
    log = []
    for tag, prompt, neg, n in GROUPS:
        print(f"== {tag} 组（{'带负面词' if neg else '纯正向'}）")
        for i in range(n):
            name = f"AYUE_{tag}{i+1}.png"
            out = os.path.join(BATCH, name)
            try:
                t0 = time.time()
                paths = agnes.gen_image(prompt, size="2K", ratio="16:9",
                                        negative=neg, save_to=out)
                dt = time.time() - t0
                for p in paths:
                    # 存提示词原文 + 参数（交接书要求）
                    with open(os.path.splitext(p)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
                        f.write(json.dumps({
                            "group": tag, "prompt": prompt, "negative": neg,
                            "size": "2K", "ratio": "16:9", "model": agnes.IMG_MODEL,
                            "elapsed_s": round(dt, 1), "file": os.path.basename(p),
                        }, ensure_ascii=False, indent=2))
                    print(f"  ✓ {os.path.basename(p)}  {dt:.0f}s")
                    log.append(p)
            except Exception as e:
                print(f"  ✗ {name}: {str(e)[:180]}")
    print(f"\n共 {len(log)} 张 → {BATCH}")
