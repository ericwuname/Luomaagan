#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
修 06 镜 —— 画面里有三只鹦鹉

⛔ 问题
   原图里：栖木上一只（主角）、窗玻璃上一只橙色的（本该是阿甘的身影）、
   右边墙上还挂着一只小的装饰。
   观众会数不清"哪只是会学话的那只"，而且"它看到骑手"这个因果铺垫废了。

   病因：prompt 只写 "notices Agan's orange silhouette through the glass"，
   模型把"橙色剪影"理解成了"另一只橙色鹦鹉"，还顺手在墙上挂了个装饰。

✅ 修法
   1. **明写只有一只鹦鹉**：`only one parrot in the entire image`
   2. **窗外是骑手的剪影**：`the blurred orange shape of a courier with a cap and backpack`
      —— 强调"背光/模糊/看不清细节"，这样模型不会去补五官
   3. **明写墙上什么都没有**：`plain wall, no decorations, no pictures`
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep02")
PARROT = os.path.join(EP, "PARROT_MASTER.png")

STYLE = ("vintage American cartoon style, thick bold black ink outlines, "
         "flat solid colors, visible halftone dot texture, "
         "warm nostalgic picture-book mood, cinematic 16:9 composition")

PROMPT = (
 "medium close shot inside a warm apartment. "
 "**ONLY ONE PARROT IN THE ENTIRE IMAGE** — "
 "**a small cartoon parrot: vivid green body, bright yellow chest, long red tail feathers, "
 "pale cream hooked beak, round black eyes, a small three-feather crest**, "
 "perched on a wooden perch. "
 "**It cranes its neck and stares at the window beside it.** "
 "**Outside the window glass, a BLURRED BACKLIT ORANGE SHAPE — only a soft silhouette of a "
 "delivery courier with a cap and a backpack, completely out of focus, no facial features "
 "visible, just an orange outline against bright daylight.** "
 "**At the edge of its attention, the parrot's head turns briefly toward the door and the "
 "doorbell beside it.** "
 "**The wall behind the perch is PLAIN — no pictures, no decorations, no other birds.** "
 "A blurred laptop and a pair of headphones sit on a desk in the background. "
 "Warm room light, " + STYLE)

if __name__ == "__main__":
    src = os.path.join(EP, "06_parrot_sees.png")
    if os.path.exists(src):
        os.rename(src, src + ".bad_3parrots")
    print("  → 06_parrot_sees 重做 ...", flush=True)
    t0 = time.time()
    agnes.gen_image(PROMPT, size="2K", ratio="16:9",
                    init_images=[PARROT], save_to=src)
    dt = time.time() - t0
    with open(os.path.join(EP, "06_parrot_sees.fix.prompt.txt"), "w", encoding="utf-8") as f:
        json.dump({"prompt": PROMPT, "elapsed_s": round(dt, 1)},
                  f, ensure_ascii=False, indent=2)
    print(f"    ✓ {dt:.0f}s  {os.path.getsize(src)//1024} KB", flush=True)
