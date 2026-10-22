#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
补拍素材 · 图生视频

配额纪律：4 段 × 7s = 28 秒，**剩下的 472 秒留给剧本定稿后**。
剧本要交给 ChatGPT 改，现在多拍会白费。

运镜写法沿用已验证的三条：
  ① 运镜放第一句，全大写
  ② 明确禁止方向（never / does not move at all）
  ③ 描述画面元素怎么变
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01d")
CLIPS = os.path.join(EP, "clips")
os.makedirs(CLIPS, exist_ok=True)

JOBS = {
 "D1_redlight": ("7",
   "**THE CAMERA IS LOCKED COMPLETELY STILL** — a fixed shot, no zoom, no pan, no drift. "
   "Inside the still frame: his chest rises and falls as he catches his breath, "
   "he tilts his head a little higher toward the sky, one ear flicks, "
   "the traffic light above **stays red then clicks to green**, "
   "the scooters around him edge forward slightly, exhaust shimmer in the air."),

 "D2_wipe": ("7",
   "**THE CAMERA IS LOCKED COMPLETELY STILL** on his face — absolutely no camera movement. "
   "He drags the back of his hand across his forehead, sweat smearing, "
   "then lets the hand drop, blinks twice, and **his mouth curves into a tired half-smile**. "
   "His cap stays slightly askew. The blurred street behind him shifts only slightly."),

 "D3_street": ("6",
   "**THE CAMERA PUSHES IN VERY SLOWLY** down the empty street, so the buildings on both "
   "sides slide outward past the frame edges and the far end of the alley grows closer. "
   "It only pushes in, never pulls back, never tilts. "
   "The hanging laundry sways gently, thin morning haze drifts across the light, "
   "a faint ripple moves through the puddle on the cobblestones. **No people appear.**"),

 "D4_stairwell": ("6",
   "**THE CAMERA TILTS UP SLOWLY** along the stairwell, from the worn concrete steps up the "
   "green peeling wall to the bare bulb at the landing. It only tilts up, never down, "
   "no zoom, no push. The bulb **flickers once and steadies**, dust drifts in the shaft of "
   "light from the dirty window, a loose handrail cable sways a little. **No people appear.**"),
}

if __name__ == "__main__":
    budget = 0
    for name, (sec, motion) in JOBS.items():
        img = os.path.join(EP, name + ".png")
        out = os.path.join(CLIPS, name + ".mp4")
        if not os.path.exists(img):
            print(f"  ! 缺 {name}.png")
            continue
        if os.path.exists(out) and os.path.getsize(out) > 80000:
            print(f"  · {name} 已存在")
            budget += int(sec)
            continue
        print(f"  → {name} ({sec}s) 配额累计 {budget+int(sec)}s ...", flush=True)
        try:
            t0 = time.time()
            agnes.gen_video(motion, seconds=sec, mode="keyframe",
                            images=[img], ratio="16:9", save_to=out)
            dt = time.time() - t0
            with open(out + ".motion.txt", "w", encoding="utf-8") as f:
                json.dump({"seconds": sec, "motion": motion,
                           "elapsed_s": round(dt, 1)}, f, ensure_ascii=False, indent=2)
            budget += int(sec)
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
        except Exception as e:
            print(f"    ✗ {str(e)[:160]}", flush=True)
    print(f"\n配额消耗 {budget}s / 500s，剩余 {500-budget}s 留给剧本定稿后", flush=True)
