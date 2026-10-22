#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
第一集 · 分镜图转视频
=====================

用 Agnes 图生视频（mode=keyframe，首帧=分镜图）。

时长（按 Gemini 分镜表，遵循 8n+1 规则）：
  S1 3.4s / S2 3.4s / S3 5s / S4 3.4s / S5 5s / S6 3.4s / S7 5s

⚠️ 实测：Agnes 视频 seconds 取 "4"–"12" 的字符串，size 只能 "720P"。
   串行跑，并发会 429。
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01")
CLIPS = os.path.join(EP, "clips")
os.makedirs(CLIPS, exist_ok=True)

MOTION = {
 "S1_alley_dawn": (
   "slow tilt down from the laundry lines to the empty alley, morning haze drifting, "
   "clothes swaying gently, sparrows hopping on the wire, dust motes in the light beam, "
   "the camera moves slowly and continuously"),

 "S2_mirror_cap": (
   "he pushes the backwards cap down onto his head, the mirror reflects the movement, "
   "then he gives a lopsided confident grin, a tiny nod, warm lamp flickers softly"),

 "S3_scooter": (
   "the scooter accelerates forward, he lifts the steaming box overhead onto the rear rack "
   "in one smooth motion, the pinwheel spins fast, ears and mane blown back, "
   "the background brick wall streaks past, a continuous forward tracking move"),

 "S4_bridge": (
   "he leans low into a sharp turn across the narrow bridge, the rhino truck rushes past "
   "in the opposite direction, the scooter's small wheel skims the iron beam, "
   "the box on the back stays perfectly level, water glitters below"),

 "S5_lobby": (
   "the dog guard taps the sign twice, the courier glances at his watch, then looks up "
   "with a sly knowing smile, cold reflections slide across the glass turnstiles"),

 "S6_elevator": (
   "he takes a slow deep breath, his thin shoulders rising and settling, "
   "both hands straighten the necktie, then he pulls his mouth up into a bright smile, "
   "the bronze walls reflect everything softly"),

 "S7_rooftop": (
   "he bites the bread roll and chews, wind lifts the tape on his ear, "
   "the camera cranes up and pulls back slowly to reveal the whole sunlit city, "
   "golden rim light, a slow continuous crane out"),
}

DUR = {"S1_alley_dawn": "4", "S2_mirror_cap": "4", "S3_scooter": "5",
       "S4_bridge": "4", "S5_lobby": "5", "S6_elevator": "4", "S7_rooftop": "5"}

if __name__ == "__main__":
    ok = 0
    for name, motion in MOTION.items():
        img = os.path.join(EP, name + ".png")
        out = os.path.join(CLIPS, name + ".mp4")
        if not os.path.exists(img):
            print(f"  ! {name} 缺首帧，跳过")
            continue
        if os.path.exists(out) and os.path.getsize(out) > 50000:
            print(f"  · {name} 已存在")
            ok += 1
            continue
        print(f"  → {name} ({DUR[name]}s) ...", flush=True)
        try:
            t0 = time.time()
            agnes.gen_video(motion, seconds=DUR[name], mode="keyframe",
                            images=[img], ratio="16:9", save_to=out)
            dt = time.time() - t0
            with open(os.path.join(CLIPS, name + ".motion.txt"), "w", encoding="utf-8") as f:
                json.dump({"motion": motion, "seconds": DUR[name],
                           "keyframe": name + ".png", "elapsed_s": round(dt, 1)},
                          f, ensure_ascii=False, indent=2)
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
            ok += 1
        except Exception as e:
            print(f"    ✗ {str(e)[:160]}", flush=True)
    print(f"\n共 {ok}/{len(MOTION)} 段 → {CLIPS}")
