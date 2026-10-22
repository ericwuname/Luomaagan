#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP01b · 分镜图转视频

运镜纪律（上一轮的血泪）：
  ① **运镜写第一句，全大写**
  ② **明确禁止方向**（never tilts up / never pulls back / does not move at all）
  ③ **描述画面元素怎么变**（frame 变宽/变窄、他变大/变小、背景往哪滑）
  → v2 实测 7 个镜头运镜全部正确（用 calib_motion.py 校准过的诊断脚本验证）

时长按剧本表，配 430 秒配额做预算。
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01b")
CLIPS = os.path.join(EP, "clips")
os.makedirs(CLIPS, exist_ok=True)

# 镜号: (秒数, motion prompt)
JOBS = {
 "S01_room": ("6", 
   "**THE CAMERA PUSHES IN SLOWLY AND CONTINUOUSLY** toward him and the mirror: "
   "the frame tightens, he becomes larger, the bed and the window slide out past the edges. "
   "It only pushes in, it never pulls back. Meanwhile he presses the small paper flag onto "
   "his cap and gives a small satisfied nod. The morning light shaft shifts faintly."),

 "S02_mirror": ("7",
   "**THE CAMERA HOLDS COMPLETELY STILL AND DOES NOT MOVE AT ALL** — a locked-off shot, "
   "no zoom, no push, no pan, the frame is fixed. Only he moves inside it: he looks at himself "
   "in the cracked mirror, then **breaks into a slightly goofy wide grin**, holding it for a "
   "moment, then a small shrug. His reflection moves with him."),

 "S03_door": ("5",
   "**THE CAMERA PUSHES IN SLOWLY** from the dark interior toward the bright open doorway, "
   "so the bright rectangle grows larger and the dark frame around it shrinks. "
   "It only moves forward, never back. Laundry in the corridor sways gently in the breeze, "
   "a neighbour in the distance moves slowly, dust motes float in the sunlight."),

 "S04_ride": ("7",
   # ⚠️ 首帧实际构图是**正面朝镜头**（不是侧跟），所以运镜必须改成"倒退跟拍"。
   #    运镜 prompt 必须服从首帧实际构图，不能按想象中的构图写。
   "**THE CAMERA MOVES BACKWARD AT THE SAME SPEED AS THE SCOOTER**, so he stays roughly "
   "the same size in the centre of frame while the brick alley walls and hanging laundry "
   "slide past on both sides and rush toward the viewer. It is a smooth retreating dolly: "
   "no zoom, no pan, no vertical bob. His ears and backpack straps flap in the wind, "
   "his front wheel wobbles slightly over the cobblestones."),

 "S05_shop": ("6",
   "**THE CAMERA HOLDS STILL** on the counter, a locked-off shot with no camera movement. "
   "Inside the frame: the clerk hurriedly slides a tray of drinks and paper bags toward him, "
   "order slips flutter, steam rises from the cups, he reaches in to take them."),

 "S06_lobby": ("7",
   "**THE CAMERA CRANES UP SLOWLY AND SLIGHTLY** while staying on him, so he stays the same "
   "size but more and more of the towering glass lobby rises into frame above him, making him "
   "feel smaller. It only cranes up, never down. The guard raises a hand and points at the "
   "sign, his arm moving decisively."),

 "S07_elevator": ("6",
   "**THE CAMERA IS LOCKED COMPLETELY STILL** — no zoom, no push, no drift, an absolutely "
   "fixed frame. Only the character moves inside it: he breathes, adjusts his grip on the "
   "white cake box, and glances up at the glowing floor numbers as they climb."),

 "S08_door_close": ("5",
   "**THE CAMERA HOLDS STILL.** The door in front of him swings shut with a soft click, "
   "cutting off the light. He stands there with empty hands, shoulders dropping slowly, "
   "the corridor bulb flickering once. No camera movement at all."),

 "S09_window": ("7",
   "**THE CAMERA PUSHES IN VERY SLOWLY** toward the lit ground-floor window, so the warm "
   "rectangle of light grows in frame and the dark street at the edges shrinks. It only pushes "
   "in, never pulls back. Inside the window a family leans over a birthday cake, laughing, "
   "balloons taped to the glass sway slightly. He sits on his scooter in the dark, watching, "
   "not moving."),

 "S10_knock": ("6",
   "**THE CAMERA PUSHES IN SLOWLY** toward the worn metal door, tightening the frame. "
   "It does not pull back. He raises one hand and knocks twice, the paper bag swinging "
   "slightly in his other hand, the bare bulb overhead swaying a little."),

 "S11_girl": ("8",
   "**THE CAMERA PUSHES IN VERY SLOWLY** through the half-open doorway toward the small girl, "
   "so she grows slightly larger in frame while the dark corridor edges recede. It only pushes "
   "in, never pulls back. The girl tilts her head up at him, birthday balloons sway behind her, "
   "warm light flickers gently on her face."),

 "S12_smile": ("6",
   "**THE CAMERA HOLDS COMPLETELY STILL** — an absolutely fixed close-up, no movement at all. "
   "Only his face moves inside the frame: he freezes for a beat, then **his eyes curve shut and "
   "he breaks into a real, warm smile**. Warm light from the open door shifts faintly across "
   "his cheek."),

 "S13_cake": ("7",
   "**THE CAMERA HOLDS STILL** on him in the dim stairwell. A woman's hand reaches out from the "
   "doorway and presses a slice of birthday cake into his hands. Warm light spills out from the "
   "flat onto his face. He looks down at the cake, then up at her, surprised."),

 "S14_steps": ("9",
   "**THE CAMERA PULLS BACK SLOWLY AND CONTINUOUSLY** away from him: the frame grows wider, he "
   "becomes smaller, and more of the empty sunset street and the old apartment block come into "
   "view around him. It only pulls out, never pushes in. Meanwhile he strikes a match and plants "
   "it upright in the cake like a candle; the tiny flame steadies and glows."),

 "S15_city": ("10",
   "**THE CAMERA CRANES UP AND PULLS BACK SLOWLY AND CONTINUOUSLY** away from him and over the "
   "city: the frame grows wider and wider, he becomes a small figure in the lower third, and the "
   "**whole dense skyline of old low houses and new glass towers is revealed, thousands of windows "
   "lighting up at dusk**. It only pulls out and rises, never pushes in, never tilts down. "
   "A thin trail of smoke rises beside him and drifts away."),
}

if __name__ == "__main__":
    budget = 0
    done = 0
    for name, (sec, motion) in JOBS.items():
        img = os.path.join(EP, name + ".png")
        out = os.path.join(CLIPS, name + ".mp4")
        if not os.path.exists(img):
            print(f"  ! 缺首帧 {name}")
            continue
        if os.path.exists(out) and os.path.getsize(out) > 80000:
            print(f"  · {name} 已存在")
            budget += int(sec)
            done += 1
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
            done += 1
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
        except Exception as e:
            print(f"    ✗ {str(e)[:160]}", flush=True)
    print(f"\n共 {done}/{len(JOBS)} 段，配额消耗约 {budget}s / 430s")
