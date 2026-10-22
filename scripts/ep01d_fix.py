#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
重做 D1/D2 —— 角色漂成了兔子，必须修

⛔ 病因
   用了 109KB 的小参考图（360×480），信息量不够，模型自己发挥成了兔子：
   耳朵翘着、脸变圆、毛色变深。

✅ 修法三条
   1. **换回原始大图参考**（864×1152 / 3MB）——现在生图只要 1-2 分钟，用得起
   2. **把"驴脸"的形状写死**：长的、直的、平的口鼻（兔子是圆的、短的）
   3. **耳朵描述**：竖直且略微后倾（兔子耳朵是翘的）
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01d")
HERO_BIG = os.path.join(ROOT, "assets", "hero", "AGAN_MASTER_2k.png")

STYLE = ("vintage American cartoon style, thick bold black ink outlines, "
         "flat solid colors, visible halftone dot texture, "
         "warm nostalgic picture-book mood, cinematic 16:9 composition")

# ★ 关键：形状写死。兔子=圆短脸+翘耳；驴骡=长直脸+竖耳
S = ("**a young hinny courier with a long straight donkey face** — "
     "**an elongated flat-fronted muzzle, squared off at the nose**, "
     "**two long upright ears held straight up and tilted slightly back** "
     "(not round, not floppy, not bent forward), "
     "slate blue-grey fur, huge round eyes with white sclera and catchlights, "
     "**an amber-orange zipped vest and an orange backpack**, "
     "slate-grey three-fingered hands, black hooves, ")

SHOTS = {
 "D1_redlight": (
   "medium shot from the side, " + S +
   "**sitting on a small yellow electric scooter stopped at a road crossing, "
   "one black hoof resting on the asphalt, head tilted up toward the sky, "
   "chest rising as he catches his breath**, "
   "other scooters waiting around him, a red traffic light glowing, "
   "long shadows across the crossing, morning light, " + STYLE),

 "D2_wipe": (
   "close medium shot, " + S +
   "**wiping his forehead with the back of one hand, his yellow cap pushed slightly askew**, "
   "eyes half shut, muzzle slightly open from breathing hard, "
   "a thin shine of sweat at his temple, street softly blurred behind, afternoon light, " + STYLE),
}

if __name__ == "__main__":
    for i, (name, prompt) in enumerate(SHOTS.items(), 1):
        old = os.path.join(EP, name + ".png")
        if os.path.exists(old):
            os.rename(old, os.path.join(EP, name + ".png.bad_rabbit"))
        out = os.path.join(EP, name + ".png")
        print(f"  → [{i}/2] {name} （大图参考）...", flush=True)
        try:
            t0 = time.time()
            agnes.gen_image(prompt, size="2K", ratio="16:9",
                            init_images=[HERO_BIG], save_to=out)
            dt = time.time() - t0
            with open(os.path.splitext(out)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
                json.dump({"prompt": prompt, "ref": "big", "elapsed_s": round(dt, 1)},
                          f, ensure_ascii=False, indent=2)
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
        except Exception as e:
            print(f"    ✗ {str(e)[:160]}", flush=True)
