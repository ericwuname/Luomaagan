#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
重做 14（出现人类）与 18（门缝没做出来）

⛔ 14 的硬伤
   画面里多了一个**穿绿衣服的人类**。这是全动物拟人世界，人类出现等于世界观破裂。
   病因：prompt 里没写"这是一个全动物世界"，模型默认补了一个人类邻居。

   同时光线也错了：剧本要求"门外走廊冷光 / 门内暖光"，但生成成了全室内暖光。

✅ 修法
   · 明写 `an all-animal anthropomorphic world, absolutely no humans`
   · 明写阿甘站在 `a cool dim CORRIDOR outside`，兔子站在 `warm lit ROOM inside`
   · 左右位置继续写死

⛔ 18 的问题
   门是整扇全开，没有"一条缝"，也没有"一双眼睛"，笑点（期待→困惑）就没了。

✅ 修法
   · 强调 `only a NARROW CRACK, just wide enough for one eye`
   · 强调 `a single eye / one pair of eyes filling the gap`
   · 强调门内区域是暗的，只有缝里透光
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
RABBIT = os.path.join(EP, "RABBIT_MASTER.png")

STYLE = ("vintage American cartoon style, thick bold black ink outlines, "
         "flat solid colors, visible halftone dot texture, "
         "warm nostalgic picture-book mood, cinematic 16:9 composition")

NO_HUMAN = ("**an all-animal anthropomorphic world — every character is an animal, "
            "absolutely NO humans anywhere in frame** ")

A = ("**a small slate blue-grey hinny courier with a long straight donkey face, cream-white "
     "squared muzzle, huge round eyes, two long upright ears, an amber-orange zipped vest, an "
     "orange delivery backpack, a yellow cap worn backwards**, ")

R = ("**an adult anthropomorphic rabbit with cream-white fur, long upright ears, round black "
     "eyes, large black over-ear headphones and a soft grey home cardigan**, ")

JOBS = {
 "14_door_open_B": ([AGAN, RABBIT],
   NO_HUMAN +
   "**medium two-shot at an open apartment door.** "
   "**On frame LEFT: the dim COOL CORRIDOR outside — dark green painted wall, old floor "
   "tiles, a bare bulb.** " + A + "**stands there on the frame left, two steps back from the "
   "doorway, in the corridor, his hooves raised slightly.** "
   "**On frame RIGHT: the doorway itself, opening INWARD into a WARM BRIGHT ROOM with amber "
   "lamplight.** " + R + "**stands inside the doorway on the frame right.** "
   "**A small paper takeaway bag stands upright on the floor between them.** "
   "The contrast between the cool corridor and the warm room is obvious, " + STYLE),

 "18_neighbors_B": ([],
   NO_HUMAN +
   "**wide corridor shot, no main character** — a narrow worn apartment corridor with chipped "
   "green walls, old floor tiles and a single bare bulb. "
   "**On frame LEFT, one apartment door is open only a NARROW CRACK — a thin vertical slit of "
   "warm light — and a single animal eye is pressed to that slit, peering out into the dark "
   "corridor.** "
   "**The eye is looking DOWNWARD, toward the floor just outside its own door, where there is "
   "nothing.** The corridor beyond the door is dark and empty. "
   "**The rest of the door stays shut.** Everything else absolutely still, " + STYLE),
}

if __name__ == "__main__":
    for name, (refs, prompt) in JOBS.items():
        out = os.path.join(EP, name + ".png")
        if os.path.exists(out) and os.path.getsize(out) > 200000:
            print(f"  · {name} 已存在")
            continue
        print(f"  → {name} [{'+'.join(os.path.basename(r)[:6] for r in refs) or '无参考'}] ...",
              flush=True)
        try:
            t0 = time.time()
            kw = dict(size="2K", ratio="16:9", save_to=out)
            if refs:
                kw["init_images"] = [r for r in refs if os.path.exists(r)]
            agnes.gen_image(prompt, **kw)
            dt = time.time() - t0
            with open(os.path.splitext(out)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
                json.dump({"prompt": prompt, "elapsed_s": round(dt, 1)},
                          f, ensure_ascii=False, indent=2)
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
        except Exception as e:
            print(f"    ✗ {str(e)[:150]}", flush=True)
