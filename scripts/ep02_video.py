#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP02 视频生成（15 段 AI 视频，另 3 镜程序渲染/复用）

运镜纪律（已在本项目验证过的三条）：
  ① 运镜写第一句，全大写
  ② 明确禁止方向（never / does not move at all）
  ③ 描述画面元素怎么变

本集三处特别处理（来自 docs/15 审查）：
  · 05 门铃：**反复强调蹄手与按钮之间有空隙**，这是全片的核心证据镜
  · 14/16 双人：**写死左右**（阿甘在画面左/门外，兔子在画面右/门内），门向内开
  · 18 门缝：**不要出现主角**，只有一扇门开一条缝和一双眼睛
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep02")
CLIPS = os.path.join(EP, "clips")
os.makedirs(CLIPS, exist_ok=True)

JOBS = {
 # ★ 素材映射修正（第一版有几镜失败，已重做）
 "02_read": ("6",
   "**THE CAMERA PUSHES IN SLOWLY** toward him, tightening the frame. It only pushes in, "
   "never pulls back. He reads the phone note, his eyes moving across the screen, "
   "then **his hoof taps the screen once and rises to his lips in a solemn hush gesture**, "
   "a small determined nod, warm afternoon light shifting on the brick wall behind him."),

 "04_tiptoe": ("6",
   "**THE CAMERA TRACKS SIDEWAYS WITH HIM toward the right**, keeping him in the same "
   "position in frame while the corridor wall slides past. It does not zoom, does not "
   "push in. He **tiptoes forward with exaggerated care**, holding the paper bag and the "
   "phone, shoulders hunched, the bag barely swaying, the bare bulb overhead flickering once."),

 # ⛔ 第一版 prompt 要求"蹄手停在一厘米外"，模型直接画成手指按上去。
 #    改用构图保证距离（门铃左上 / 蹄子右下 / 中间大片空白），motion 也要跟着改。
 "05_bell_A": ("5",
   "**THE CAMERA IS LOCKED COMPLETELY STILL** — no zoom, no pan, no drift. "
   "**The hoof in the lower right of frame trembles once, drifts slightly toward the bell "
   "and then STOPS, and withdraws out of frame. It never reaches the button.** "
   "**The large empty gap between the hoof and the doorbell stays empty for the whole shot, "
   "the button stays dark and unlit.** Only the hoof moves."),

 "06_parrot_sees": ("5",
   "**THE CAMERA IS LOCKED STILL** on the parrot, no zoom, no pan. "
   "It **cranes its neck and stares out through the window glass at something outside, "
   "head cocked sharply to one side**, an eye blinking, then **its head turns briefly "
   "toward the door and the doorbell beside it, then back out the window**. "
   "Blurred laptop and headphones behind it, warm room light."),

 "07_bag": ("6",
   "**THE CAMERA TILTS DOWN SLOWLY** following him as he kneels, so more of the floor and "
   "the bag enter the frame. It only tilts down, never up. He **sets the paper bag down "
   "beside the door and straightens it with both hooves so it stands upright**, "
   "then begins to back away on his toes. The door stays closed, the doorbell stays dark."),

 "08_parrot_bell": ("6",
   "**THE CAMERA IS LOCKED STILL** on the parrot. It **suddenly throws its head back, "
   "beak wide open mid-shout, chest puffed out round, wings lifted slightly**, "
   "then settles and **looks extremely pleased with itself**, chest still puffed. "
   "The same perch and window as before. No camera movement at all."),

 "09_shock": ("5",
   "**THE CAMERA PUSHES IN QUICKLY AND STOPS** — a short fast push that halts. "
   "He **freezes mid-step, both ears snap straight upright, eyes go wide and turn toward "
   "the door, mouth falls slightly open**, then he **slowly looks down at the phone in his "
   "hoof and toward the dark doorbell button**. Hold on his baffled face."),

 "10_rabbit_call": ("6",
   "**THE CAMERA IS LOCKED STILL** in the warm apartment. The rabbit **flinches at the sound, "
   "then raises one paw with a single finger pressed to its lips and points urgently toward "
   "the window with the other paw**, shoulders hunched, glancing back at the laptop screen. "
   "The lamp behind flickers slightly. No camera movement."),

 "11_parrot_mimic": ("6",
   "**THE CAMERA PUSHES IN SLOWLY** toward the parrot. It **leans forward, beak opening wide, "
   "one wing lifted for balance, and bounces once on the perch as it squawks**, "
   "body angled toward the doorway, **eager and delighted rather than malicious**. "
   "It only pushes in, never pulls back."),

 "12_whisper": ("6",
   "**THE CAMERA IS LOCKED STILL** on him crouched beside the corridor wall. "
   "He **cups one hoof near his mouth and whispers toward the closed door, his body leaning "
   "away from the doorbell, eyes darting sideways nervously**, shoulders tense. "
   "The bare bulb above him flickers once. No camera movement."),

 "13_parrot_loud": ("5",
   "**THE CAMERA IS LOCKED STILL** on the parrot. It **spreads both wings wide open, "
   "beak open as far as it will go, chest fully puffed, the feathers on its crest standing "
   "straight up**, holding the pose at maximum volume. Warm room light from behind. "
   "Absolutely no camera movement."),

 # ⛔ 第一版出现了人类（硬伤）。重做版用"全动物世界"明写排除。
 "14_door_open_B": ("7",
   "**THE CAMERA IS LOCKED STILL** on the doorway. "
   "**The apartment door swings INWARD into the warm room.** "
   "**The rabbit steps into the doorway on frame RIGHT**, looking down at the paper bag on "
   "the floor and then across at Agan. "
   "**Agan stays on frame LEFT, outside in the cool dim corridor, two steps back, hooves "
   "raised slightly.** Warm interior light spills out; the corridor stays cool green. "
   "The bag never moves. **No humans appear — every character is an animal.** "
   "No camera movement."),

 "16_triangle": ("6",
   "**THE CAMERA IS LOCKED STILL** on a three-subject composition through the open doorway. "
   "**The rabbit stands on frame RIGHT in the doorway; the parrot perches just inside the "
   "room beside the doorway; Agan stands on frame LEFT outside in the corridor.** "
   "**Agan and the rabbit turn their heads toward the bird at the same moment.** "
   "The parrot **puffs its chest and opens its beak wide**. No camera movement."),

 "17_fivestar": ("6",
   "**THE CAMERA PUSHES IN SLOWLY** toward the rabbit and the phone. The rabbit **exhales "
   "visibly, taps the phone screen once, then gives a small apologetic thumbs-up toward the "
   "corridor**, shoulders relaxing. **Five stars light up on the phone screen.** "
   "It only pushes in, never pulls back."),

 # ⛔ "门缝+一双眼睛"两次都没做出来。不再死磕：
 #    保留走廊 + 一扇开着缝的门，**靠声音（三声门轴响）让观众"听到"整层楼开门**。
 #    这比硬生成一群动物可靠得多，笑点也保住了。
 "18_neighbors_B": ("7",
   "**THE CAMERA IS LOCKED STILL, then PULLS BACK VERY SLIGHTLY at the end.** "
   "The narrow corridor stays empty. "
   "**The door on frame LEFT, already ajar with a thin slit of warm light, opens a little "
   "wider — the slit of light grows from a thin line to a narrow wedge** — and then holds. "
   "**No character appears; the corridor stays empty.** "
   "The bare bulb overhead flickers once, dust drifts in the light. "
   "**No humans. No animals. Just an empty corridor with one door standing ajar.**"),
}

if __name__ == "__main__":
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    budget, done, fail = 0, 0, []
    for name, (sec, motion) in JOBS.items():
        if only and not any(o in name for o in only):
            continue
        img = os.path.join(EP, name + ".png")
        out = os.path.join(CLIPS, name + ".mp4")
        if not os.path.exists(img):
            print(f"  ! 缺首帧 {name}")
            continue
        if os.path.exists(out) and os.path.getsize(out) > 80000:
            print(f"  · {name} 已存在")
            budget += int(sec); done += 1
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
            budget += int(sec); done += 1
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
        except Exception as e:
            print(f"    ✗ {str(e)[:160]}", flush=True)
            fail.append(name)
    print(f"\n完成 {done}/{len(JOBS)}，配额 {budget}s / 500s" +
          (f"，失败：{fail}" if fail else ""), flush=True)
