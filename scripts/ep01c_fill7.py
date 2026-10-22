#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP01c《第一万单》· 只补 7 张新镜（其余复用 ep01b）

⛔ 时间现实：单张首帧要 5 分钟以上（API 队列慢，跟是否传参考图无关）。
   26 镜全做要 4 小时，不可行。

✅ 解法：**复用 ep01b 已生成的 13 个镜头**，只补"三单"缺的 7 张。

素材映射：
  S01 手机 9996   ← render_phone（程序渲染）
  S02 出租屋贴旗   ← ep01b/S01_room
  S03 镜子笑      ← ep01b/S02_mirror
  S04 手机 9997   ← render_phone
  S05 骑车出门     ← ep01b/S04_ride
  S06 蛋糕店取单   ← **新**
  S07 送到一家人   ← **新**
  S08 转身        ← **新**
  S09 花店买花     ← **新**
  S10 送到求婚男   ← **新**
  S11 玩具取件     ← **新**
  S12 送到父子     ← **新**
  S13 楼道听笑     ← ep01b/S09_window（窗外看别人过生日）
  S14 手机 10000  ← render_phone
  S15 敲门       ← ep01b/S10_knock
  S16 开门小女孩   ← ep01b/S11_girl
  S17 愣住笑      ← ep01b/S12_smile
  S18 妈妈塞蛋糕   ← ep01b/S13_cake
  S19 台阶火柴     ← ep01b/S14_steps
  S20 城市        ← ep01b/S15_city
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01c")
os.makedirs(EP, exist_ok=True)
HERO = os.path.join(ROOT, "assets", "hero", "AGAN_MASTER_2k.png")

# 小参考图（123KB vs 3MB，上传快得多）
SMALL = os.path.join(EP, "_ref480.png")
if not os.path.exists(SMALL):
    im = Image.open(HERO).convert("RGB")
    im.thumbnail((440, 440), Image.LANCZOS)
    im.save(SMALL, "PNG", optimize=True)

STYLE = ("vintage American cartoon style, thick bold black ink outlines, "
         "flat solid colors, visible halftone dot texture, "
         "warm nostalgic picture-book mood, cinematic 16:9 composition")

D = ("**a small cartoon hinny delivery courier**: slate blue-grey fur, a cream-white squarish "
     "muzzle with two black oval nostrils, huge round eyes with white sclera and catchlights, "
     "two long upright ears with pale grey inner surfaces, a thin curved smile, "
     "**an amber-orange zipped vest and an orange backpack**, three-fingered grey hands, "
     "black hooves, a thin tail with a black tuft, ")

S = ("**the same slate blue-grey hinny courier in the amber-orange vest, cream muzzle, "
     "huge round eyes and long ears**, ")

SHOTS = {
 "S06_cakeshop": "medium shot at a bakery service window, " + S +
   "**receiving a white cake box tied with a ribbon through the window**, "
   "a baker's hands pushing it out to him, warm bakery light, pastry trays behind, " + STYLE,

 "S07_family": "shot through an open apartment door, " + S +
   "seen from behind at the left edge handing over the cake box, "
   "**inside a warm bright flat a family gathers around a table, a small child jumping up with "
   "both arms raised shouting with joy**, balloons and paper garlands, "
   "warm orange light flooding out into the dim corridor, " + STYLE,

 "S08_turn": "medium wide shot, " + S +
   "**standing alone in a dim apartment corridor, the door shut behind him, body half turned "
   "away mid-step, glancing back once over his shoulder**, empty hands, "
   "single overhead bulb, long shadow, " + STYLE,

 "S09_flower": "medium shot at a small flower shop, " + S +
   "**receiving a big bunch of red roses wrapped in kraft paper**, the florist's hands passing "
   "it across the counter, buckets of flowers all around, soft light, " + STYLE,

 "S10_propose": "medium shot in an office corridor, " + S +
   "**handing a bunch of red roses to a young man in a shirt**, the man taking them with both "
   "hands, nervous happy grin, glass office walls, cool daylight, " + STYLE,

 "S11_toybox": "medium shot at a parcel counter, " + S +
   "**lifting a large cardboard toy box with both arms, the box almost as wide as he is**, "
   "shop assistant behind the counter, warm indoor light, " + STYLE,

 "S12_father": "shot through an open door, " + S +
   "seen from behind at the left edge handing over a big toy box, "
   "**a father takes it while a small child rushes out and hugs his father's leg**, "
   "warm evening light from inside the flat, " + STYLE,
}

if __name__ == "__main__":
    print(f"小参考图 {os.path.getsize(SMALL)//1024} KB", flush=True)
    for i, (name, prompt) in enumerate(SHOTS.items(), 1):
        out = os.path.join(EP, name + ".png")
        if os.path.exists(out) and os.path.getsize(out) > 200000:
            print(f"  · [{i}/7] {name} 已存在", flush=True)
            continue
        print(f"  → [{i}/7] {name} ...", flush=True)
        try:
            t0 = time.time()
            agnes.gen_image(prompt, size="2K", ratio="16:9",
                            init_images=[SMALL], save_to=out)
            dt = time.time() - t0
            with open(os.path.splitext(out)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
                json.dump({"prompt": prompt, "ref": "small480",
                           "elapsed_s": round(dt, 1)}, f, ensure_ascii=False, indent=2)
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
        except Exception as e:
            print(f"    ✗ {str(e)[:150]}", flush=True)
    print(f"\n→ {EP}", flush=True)
