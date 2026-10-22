#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
第一集 · 分镜图转视频（v2 —— 修正运动方向）

⛔ 为什么重做（用户："运动方向不对"）
   实测诊断（scripts/diag_motion.py）：
     S1 要求下摇 → 实际**上摇**
     S2 要求推镜 → 实际**拉远**
     S3 要求侧跟平移 → 实际**原地上下晃**
     S6 要求固定   → 实际**推近**
     S7 要求拉远   → 实际只下摇，**没有拉远**
   7 个镜头 6 个方向错。

⛔ 根因：我违反了《走蛟》铁律 —— **prompt 第一句必须是摄影机运动**。
   上一版我把运镜写在最后一句，模型专心做人物动作，运镜就飘了。

✅ 本版三条改法：
   1. **运镜放第一句，全大写**
   2. **明确"不要往哪动"**（never up / never pulls back / does not move at all）
   3. **描述画面元素怎么变**（frame 变宽/变窄、背景往哪滑、他变大/变小）
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01")
CLIPS = os.path.join(EP, "clips_v2")
os.makedirs(CLIPS, exist_ok=True)

# 每一条第一句都是运镜，大写，带方向 + 禁止方向 + 画面元素变化
MOTION = {
 "S1_alley_dawn":
   "**THE CAMERA TILTS DOWN** slowly and continuously: start looking at the laundry poles "
   "and the sparrows high on the wire, then tilt DOWN the brick walls until the empty alley "
   "floor fills the bottom of frame. The camera tilts only DOWNWARD, it never tilts up. "
   "The clothes sway, morning haze drifts, dust floats in the light. Continuous single move.",

 "S2_mirror_cap":
   "**THE CAMERA DOLLIES IN** slowly and continuously toward his face: the frame grows tighter, "
   "his head becomes larger in frame, the walls and furniture slide OUT past the edges. "
   "The camera only moves FORWARD, it never pulls back and never zooms out. "
   "Meanwhile he pushes the backwards cap down onto his head and gives a lopsided grin. "
   "Continuous single move.",

 "S3_scooter":
   "**THE CAMERA TRACKS SIDEWAYS TO THE RIGHT** at exactly the scooter's speed, "
   "so the scooter stays pinned in the centre of frame while the entire background street "
   "slides from RIGHT to LEFT behind him. This is a pure sideways tracking shot: "
   "no zoom, no push in, no vertical movement, no up-and-down bobbing. "
   "He lifts the steaming box onto the rear rack, the pinwheel spins, his ears blow back. "
   "One long uninterrupted sideways track.",

 "S4_bridge":
   "**THE CAMERA STAYS LOW NEAR THE BRIDGE DECK LOOKING UP** and rotates slightly to the RIGHT "
   "to follow his turn. The camera stays at this low height for the whole shot: it does not rise, "
   "does not crane up, does not tilt up. He leans low into the tight turn, the rhino truck rushes "
   "past the opposite way, the small wheel skims the iron beam, the box stays level, "
   "water glitters far below. Continuous single move.",

 "S5_lobby":
   "**THE CAMERA SITS LOW LOOKING UP** at the turnstiles, and PUSHES IN very slowly toward the "
   "courier, then holds still. It does not pull back. The dog guard taps the sign twice, "
   "the courier glances at his watch then looks up with a sly smile, cold reflections slide "
   "across the glass. Continuous single move.",

 "S6_elevator":
   "**THE CAMERA IS LOCKED COMPLETELY STILL ON A TRIPOD AND DOES NOT MOVE AT ALL** — "
   "no zoom, no push, no pan, no drift, the frame is absolutely fixed for the entire shot. "
   "Only the character moves inside the still frame: he takes a slow deep breath, "
   "his thin shoulders rise and settle, both hands straighten the necktie, "
   "then he pulls his mouth up into a bright smile. Bronze walls reflect everything softly. "
   "The camera stays motionless the whole time.",

 "S7_rooftop":
   "**THE CAMERA CRANES UP AND PULLS BACK** slowly and continuously away from him: "
   "the frame grows wider and wider, he becomes smaller and smaller in the middle of frame, "
   "and more and more of the sunlit city is revealed below and beyond. "
   "The camera only pulls OUT and rises, it never pushes in and never tilts down. "
   "He bites the bread roll and chews, the wind lifts the tape on his ear, "
   "golden rim light. One long continuous crane-out.",
}

DUR = {"S1_alley_dawn": "4", "S2_mirror_cap": "4", "S3_scooter": "5",
       "S4_bridge": "4", "S5_lobby": "5", "S6_elevator": "4", "S7_rooftop": "5"}

if __name__ == "__main__":
    ok = 0
    for name, motion in MOTION.items():
        img = os.path.join(EP, name + ".png")
        out = os.path.join(CLIPS, name + ".mp4")
        if not os.path.exists(img):
            print(f"  ! {name} 缺首帧")
            continue
        if os.path.exists(out) and os.path.getsize(out) > 80000:
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
