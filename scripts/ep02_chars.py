#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP02 新角色定妆：鹦鹉 + 兔子住户

剧本要求（story/EP02_别敲门.md B 节）：
  鹦鹉：绿色身体、黄色胸部、红色尾羽，站在室内靠近门窗的栖木上。
        不是会思考的反派，只会把听到的声音和短句不断复读。
  兔子：成年拟人兔子，戴耳机参加线上会议，想要安静，不是坏人。

⛔ 为什么先定妆
   这两个角色要出现在 5+4 个镜头里。不定妆就逐镜生成，每镜一个样，
   观众会以为是不同的鸟/不同的兔子。

做法：每个角色出一张标准照（正侧 3/4 视角，可看清特征），
      后续所有镜头都以它为 I2I 参考。
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep02")
os.makedirs(EP, exist_ok=True)

STYLE = ("vintage American cartoon style, thick bold black ink outlines, "
         "flat solid colors, visible halftone dot texture, "
         "warm nostalgic picture-book mood, clean character-sheet composition")

CHARS = {
 "PARROT_MASTER": (
   "**character reference sheet of a small cartoon parrot**, single subject, "
   "three-quarter view, standing on a wooden perch, full body visible. "
   "**vivid green body, bright yellow chest, long red tail feathers**, "
   "a pale cream beak with a dark hook at the tip, "
   "round black eyes with white catchlights, a small crest of three feathers on the head, "
   "grey scaly feet gripping the perch, "
   "**extremely simple shapes, big head, tiny body**, expressive and slightly smug. "
   "Plain warm cream background, " + STYLE),

 "RABBIT_MASTER": (
   "**character reference sheet of an adult anthropomorphic rabbit**, single subject, "
   "three-quarter view, standing, full body visible. "
   "**cream-white fur with pale grey inner ears, two long upright ears**, "
   "round black eyes with white catchlights, a small pink nose, two prominent front teeth, "
   "**wearing large black over-ear headphones and a soft grey home cardigan**, "
   "holding a laptop under one arm, "
   "tired but decent and polite, not a villain. "
   "Plain warm cream background, " + STYLE),
}

if __name__ == "__main__":
    for name, prompt in CHARS.items():
        out = os.path.join(EP, name + ".png")
        if os.path.exists(out) and os.path.getsize(out) > 200000:
            print(f"  · {name} 已存在")
            continue
        print(f"  → {name} ...", flush=True)
        try:
            t0 = time.time()
            agnes.gen_image(prompt, size="2K", ratio="3:4", save_to=out)
            dt = time.time() - t0
            with open(os.path.splitext(out)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
                json.dump({"prompt": prompt, "elapsed_s": round(dt, 1)},
                          f, ensure_ascii=False, indent=2)
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
        except Exception as e:
            print(f"    ✗ {str(e)[:150]}", flush=True)
