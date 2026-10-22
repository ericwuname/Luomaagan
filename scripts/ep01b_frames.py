#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP01《今天的生日》· 分镜首帧生成
===============================

角色来源：用户提供的 Claude D 方案定稿图 → assets/hero/AGAN_MASTER_2k.png
从图里取到的精确色板：
  灰蓝毛 #708080 / 橙背心 #F0A010 / 米白口鼻 #E0D0C0 / 粗黑描边 / 网点

⛔ 上一版踩过的坑：给"空镜"传 I2I 参考，模型会把角色硬画进去。
   所以本脚本区分两类：
     有角色的镜头 → 传 I2I 参考（锁身份）
     空镜         → 不传，纯文生图
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01b")
os.makedirs(EP, exist_ok=True)
HERO = os.path.join(ROOT, "assets", "hero", "AGAN_MASTER_2k.png")

STYLE = ("vintage American cartoon style, thick bold black ink outlines, "
         "flat solid colors, visible halftone dot texture, "
         "warm nostalgic picture-book mood, 16:9 cinematic composition")

# ★ 角色锚点：精确到色值和形状，全部来自用户给的那张图
HERO_DESC = ("**a small cartoon hinny delivery courier** — "
             "**slate blue-grey fur** , "
             "**a cream-white squarish muzzle** with two black oval nostrils on its top, "
             "**very large round eyes** with big white sclera, black pupils and white catchlights, "
             "**two long upright ears** with pale grey inner surfaces, "
             "a simple thin curved line as a smile, "
             "**an amber-orange zipped vest**, "
             "**an orange backpack**, "
             "slate-grey three-fingered hands, black hooves, "
             "a thin tail with a black tuft at the tip, ")

HERO_SHORT = ("**the same slate blue-grey hinny courier with the cream muzzle, "
              "huge round eyes, long ears and amber-orange vest** ")

# ── 15 个镜头 ──
# ref=True 传角色参考；ref=False 是空镜
SHOTS = {
 "S01_room": dict(ref=True, ratio="16:9",
   prompt="medium shot, inside a tiny rented room at dawn, " + HERO_DESC +
          "standing in front of **a cracked old mirror**, pressing a small homemade paper flag "
          "onto the brim of his cap, a single warm shaft of morning light cutting across the wall, "
          "a narrow bed, a kettle, clothes on a line, cramped and poor but tidy, "
          + STYLE),

 "S02_mirror": dict(ref=True, ratio="16:9",
   prompt="close medium shot, " + HERO_DESC +
          "looking at himself in **a cracked mirror**, breaking into a slightly goofy wide grin, "
          "the mirror shows his reflection slightly offset, warm lamp light on one side, "
          "a piece of faded tape visible on one ear, " + STYLE),

 "S03_door": dict(ref=False, ratio="16:9",
   prompt="wide shot from behind, **an open doorway of a cramped old apartment opening onto "
          "a narrow outdoor corridor**, laundry hanging across the corridor, a neighbour "
          "brushing teeth in the distance, strong morning sunlight flooding in from outside, "
          "**no characters, empty corridor, seen from inside the dark room looking out**, "
          "the dark interior frames the bright doorway, " + STYLE),

 "S04_ride": dict(ref=True, ratio="16:9",
   prompt="side tracking action shot, " + HERO_DESC +
          "riding a small yellow electric scooter fast down an old-town alley, "
          "**his orange backpack bulging**, ears blown back by the wind, leaning forward, "
          "old brick walls and hanging laundry streaking past, morning glare, " + STYLE),

 "S05_shop": dict(ref=True, ratio="16:9",
   prompt="medium wide shot, inside a crowded bubble-tea shop counter, " + HERO_SHORT +
          "standing at the counter while a hurried clerk pushes a tray of drink cups and "
          "paper bags toward him, a row of order slips clipped above, warm shop light, "
          "busy and slightly chaotic, " + STYLE),

 "S06_lobby": dict(ref=True, ratio="16:9",
   prompt="wide low angle shot, " + HERO_SHORT +
          "small in frame before a tall glass office lobby, **a big stern dog security guard "
          "in uniform raising one hand to block him** and pointing at a sign on the wall, "
          "cold teal-grey lighting, polished stone floor reflections, "
          "**the tiny courier dwarfed by the architecture**, " + STYLE),

 "S07_elevator": dict(ref=True, ratio="16:9",
   prompt="tight enclosed elevator shot, " + HERO_SHORT +
          "standing against the mirrored wall **holding a white cake box with both arms**, "
          "floor numbers glowing above, amber reflections on bronze surfaces, "
          "his eyes looking down at the box, quiet and alone, " + STYLE),

 "S08_door_close": dict(ref=True, ratio="16:9",
   prompt="medium shot, " + HERO_SHORT +
          "standing in an apartment corridor, **his hands now empty at his sides**, "
          "facing a closed door, **the door has just shut**, dim corridor light from above, "
          "his shoulders slightly dropped, quiet disappointment, " + STYLE),

 "S09_window": dict(ref=True, ratio="16:9",
   prompt="medium wide shot at dusk, " + HERO_SHORT +
          "**sitting on his scooter stopped on the street, looking through a lit ground-floor "
          "window where a family gathers around a birthday cake, laughing, balloons taped to "
          "the glass**, warm orange light spilling out of the window onto the dark street, "
          "he is in shadow, watching, " + STYLE),

 "S10_knock": dict(ref=True, ratio="16:9",
   prompt="medium shot, dim old apartment stairwell, " + HERO_SHORT +
          "standing before a worn metal door, one hand raised to knock, "
          "**a paper bag of food in the other hand**, a single bare bulb overhead, "
          "green-painted walls, narrow and shadowy, " + STYLE),

 "S11_girl": dict(ref=True, ratio="16:9",
   prompt="over-the-shoulder shot through a half-open door, " + HERO_SHORT +
          "seen from behind at the left edge, **a small girl with braided hair standing in the "
          "doorway looking up at him**, warm orange birthday-party light and balloons behind her "
          "inside the flat, the corridor dark, gentle contrast, " + STYLE),

 "S12_smile": dict(ref=True, ratio="16:9",
   prompt="close-up, " + HERO_DESC +
          "**frozen for a moment, then breaking into a real smile, eyes curving shut with "
          "happiness**, warm light from the open door falling on his face, "
          "soft halftone shading, deeply tender, " + STYLE),

 "S13_cake": dict(ref=True, ratio="16:9",
   prompt="medium close shot, " + HERO_SHORT +
          "in a dim stairwell, **a woman's hand reaching out from the doorway pressing a slice "
          "of birthday cake into his hands**, warm light spilling from the flat, "
          "he is looking down at the cake, surprised and moved, " + STYLE),

 "S14_steps": dict(ref=True, ratio="16:9",
   prompt="medium wide shot, " + HERO_SHORT +
          "**sitting alone on concrete steps outside an old apartment block at sunset**, "
          "a slice of cake on his knees, **striking a match and planting it upright in the cake** "
          "like a candle, the flame tiny and bright, long warm shadows, "
          "empty street, deeply quiet, " + STYLE),

 "S15_city": dict(ref=True, ratio="16:9",
   prompt="epic wide shot from a low rooftop, " + HERO_SHORT +
          "**seen small in the lower third of frame from behind, head tilted up**, "
          "**a vast dense city of old low houses and new glass towers packed together, "
          "thousands of windows lit up at sunset**, a thin trail of smoke rising beside him, "
          "golden and blue dusk sky, deeply emotional and hopeful, " + STYLE),
}

if __name__ == "__main__":
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    for name, cfg in SHOTS.items():
        if only and not any(o in name for o in only):
            continue
        out = os.path.join(EP, name + ".png")
        if os.path.exists(out) and os.path.getsize(out) > 200000:
            print(f"  · {name} 已存在")
            continue
        print(f"  → {name} {'[参考]' if cfg['ref'] else '[空镜]'} ...", flush=True)
        try:
            t0 = time.time()
            kw = dict(size="2K", ratio=cfg["ratio"], save_to=out)
            if cfg["ref"]:
                kw["init_images"] = [HERO]
            agnes.gen_image(cfg["prompt"], **kw)
            dt = time.time() - t0
            with open(os.path.splitext(out)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
                json.dump({"prompt": cfg["prompt"], "ref": cfg["ref"],
                           "ratio": cfg["ratio"], "elapsed_s": round(dt, 1)},
                          f, ensure_ascii=False, indent=2)
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
        except Exception as e:
            print(f"    ✗ {str(e)[:150]}", flush=True)
    print(f"\n→ {EP}")
