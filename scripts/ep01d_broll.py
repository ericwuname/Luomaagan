#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
补拍「通用素材」—— 不绑定具体剧情，任何版本剧本都能用

⛔ 为什么挑这些
   用户的剧本要交给 ChatGPT 优化，剧情细节随时会变。
   拍"送花给求婚男"这种镜头，剧本一改就废。
   所以只拍**纯环境 / 骑手体感**的镜头：

   1. 等红灯（停下车，抬头喘气）      —— 劳动者的体感，任何外卖故事都要
   2. 擦汗（用手背抹额头，帽子歪了）  —— 同上
   3. 城市空镜（清晨老街，无人）      —— 转场 / 开场 / 结尾都能用
   4. 楼道空镜（旧楼楼梯，灯泡闪）    —— 转场 / 铺垫都用得上

   这四个是"底片素材"，剪进哪一版都成立。
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01d")
os.makedirs(EP, exist_ok=True)
REF = os.path.join(ROOT, "work", "ep01c", "_ref480.png")
if not os.path.exists(REF):
    REF = os.path.join(ROOT, "assets", "hero", "AGAN_MASTER_2k.png")

STYLE = ("vintage American cartoon style, thick bold black ink outlines, "
         "flat solid colors, visible halftone dot texture, "
         "warm nostalgic picture-book mood, cinematic 16:9 composition")

S = ("**a small slate blue-grey hinny courier in an amber-orange zipped vest with an orange "
     "backpack, cream-white muzzle, huge round eyes, two long upright ears**, ")

SHOTS = {
 # ── 有角色的体感镜头（传参考）──
 "D1_redlight": (True,
   "medium shot from the side, " + S +
   "**sitting on a small yellow electric scooter stopped at a crossing, one black hoof resting "
   "on the road, head tilted up to the sky, chest rising as he catches his breath**, "
   "other scooters waiting around him, morning traffic light glowing red, "
   "long shadows across the asphalt, " + STYLE),

 "D2_wipe": (True,
   "close medium shot, " + S +
   "**wiping his forehead with the back of one hand, the yellow cap pushed slightly askew**, "
   "eyes half shut, mouth slightly open from breathing hard, a thin line of sweat at his "
   "temple, street softly blurred behind, afternoon light, " + STYLE),

 # ── 纯环境空镜（不传参考，避免把角色画进去）──
 "D3_street": (False,
   "wide establishing shot at dawn, **an empty old-town street, no people at all**, "
   "low brick buildings with drying laundry hanging from upper windows, "
   "a single abandoned paper cup on the wet cobblestones, "
   "warm low sunlight cutting between the buildings, thin morning haze, "
   "quiet and still, " + STYLE),

 "D4_stairwell": (False,
   "wide interior shot, **an empty dark apartment stairwell, no people**, "
   "green-painted walls with peeling paint, a bare bulb flickering at the landing, "
   "worn concrete steps, a bicycle parked under the stairs, "
   "dim light from a dirty window above, quiet and slightly melancholy, " + STYLE),
}

if __name__ == "__main__":
    print(f"参考图 {os.path.getsize(REF)//1024} KB", flush=True)
    for i, (name, (use_ref, prompt)) in enumerate(SHOTS.items(), 1):
        out = os.path.join(EP, name + ".png")
        if os.path.exists(out) and os.path.getsize(out) > 200000:
            print(f"  · [{i}/4] {name} 已存在", flush=True)
            continue
        print(f"  → [{i}/4] {name} {'[参考]' if use_ref else '[空镜]'} ...", flush=True)
        try:
            t0 = time.time()
            kw = dict(size="2K", ratio="16:9", save_to=out)
            if use_ref:
                kw["init_images"] = [REF]
            agnes.gen_image(prompt, **kw)
            dt = time.time() - t0
            with open(os.path.splitext(out)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
                json.dump({"prompt": prompt, "ref": use_ref,
                           "elapsed_s": round(dt, 1)}, f, ensure_ascii=False, indent=2)
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
        except Exception as e:
            print(f"    ✗ {str(e)[:150]}", flush=True)
    print(f"\n→ {EP}", flush=True)
