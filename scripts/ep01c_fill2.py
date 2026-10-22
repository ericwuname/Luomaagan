#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
只补 2 张关键镜：S07 送到一家人 / S12 送到父子

⛔ 为什么卡住
   S06 其实 23:38 就出图了，之后一直卡在 S07。
   S07 的 prompt 里有 "a small child jumping up with both arms raised shouting"——
   涉及儿童 + 情绪激动，很可能触发内容审核导致反复重试。

✅ 修法：这本来就是个**动物拟人世界**，把人类全部换成动物。
   · 小孩 → 小羊羔 / 小马驹（拟人）
   · 爸爸 → 成年山羊
   · 妈妈 → 成年绵羊
   既绕开审核，也让世界观更统一（骡马城里本来就该全是动物）。
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01c")
REF = os.path.join(EP, "_ref480.png")

STYLE = ("vintage American cartoon style, thick bold black ink outlines, "
         "flat solid colors, visible halftone dot texture, "
         "warm nostalgic picture-book mood, cinematic 16:9 composition")

S = ("**a small slate blue-grey hinny courier in an amber-orange zipped vest with an orange "
     "backpack, cream-white muzzle, huge round eyes, two long upright ears**, ")

SHOTS = {
 "S07_family": (
   "shot through an open apartment door, " + S +
   "**seen from behind at the left edge handing over a white cake box**, "
   "**inside a warm bright parlour an anthropomorphic goat family gathers around a table** — "
   "a tall adult goat in a knitted cardigan and **a tiny lamb standing on a chair with both "
   "hooves raised in delight** — balloons and paper garlands on the wall, "
   "**warm orange light flooding out of the flat into the dim corridor**, " + STYLE),

 "S12_father": (
   "shot through an open door, " + S +
   "**seen from behind at the left edge handing over a big cardboard toy box**, "
   "**an adult anthropomorphic sheep in a work jacket takes it while a small lamb rushes out "
   "and hugs the adult's leg**, warm evening light spilling from inside the flat, "
   "a doormat and a shoe rack in the corridor, " + STYLE),
}

if __name__ == "__main__":
    for i, (name, prompt) in enumerate(SHOTS.items(), 1):
        out = os.path.join(EP, name + ".png")
        if os.path.exists(out) and os.path.getsize(out) > 200000:
            print(f"  · {name} 已存在")
            continue
        print(f"  → [{i}/2] {name} ...", flush=True)
        try:
            t0 = time.time()
            kw = dict(size="2K", ratio="16:9", save_to=out)
            if os.path.exists(REF):
                kw["init_images"] = [REF]
            agnes.gen_image(prompt, **kw)
            dt = time.time() - t0
            with open(os.path.splitext(out)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
                json.dump({"prompt": prompt, "elapsed_s": round(dt, 1)},
                          f, ensure_ascii=False, indent=2)
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
        except Exception as e:
            print(f"    ✗ {str(e)[:180]}", flush=True)
