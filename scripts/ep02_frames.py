#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP02《别敲门，鹦鹉会替你》· 15 镜首帧

剧本：story/EP02_别敲门.md（GPT 稿）+ docs/15 审查意见的 3 处修改

审查后的修改已并入本脚本：
  修改1 · 06 镜末尾：鹦鹉看完阿甘后**转头瞟向门和门铃**（补上"它为什么学门铃"这一环）
  修改3 · 02 镜台词补"记得五星好评"（给 16 镜鹦鹉学这句话找到出处）
  修改2 · 18 镜：邻居**先眼睛发亮、看向自己门口地面，然后表情垮掉**（不是傻看阿甘）

参考图用法（三级）：
  · 阿甘镜头      → AGAN_MASTER_2k.png（大图，实测比小图保特征）
  · 鹦鹉镜头      → PARROT_MASTER.png
  · 兔子镜头      → RABBIT_MASTER.png
  · 双人/三人     → 传阿甘 + 对方（多图参考；失败则退化为阿甘单图）
  · 空镜/门缝     → **不传任何参考**（传了会把角色画进去）
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep02")
os.makedirs(EP, exist_ok=True)

AGAN = os.path.join(ROOT, "assets", "hero", "AGAN_MASTER_2k.png")
PARROT = os.path.join(EP, "PARROT_MASTER.png")
RABBIT = os.path.join(EP, "RABBIT_MASTER.png")

STYLE = ("vintage American cartoon style, thick bold black ink outlines, "
         "flat solid colors, visible halftone dot texture, "
         "warm nostalgic picture-book mood, cinematic 16:9 composition")

A = ("**a small slate blue-grey hinny courier with a long straight donkey face, cream-white "
     "squared muzzle, huge round eyes, two long upright ears, a faded yellow tape ring on his "
     "left ear, an amber-orange zipped vest, an orange delivery backpack, a yellow cap worn "
     "backwards**, ")

P = ("**a small cartoon parrot: vivid green body, bright yellow chest, long red tail feathers, "
     "pale cream hooked beak, round black eyes, a small three-feather crest**, ")

R = ("**an adult anthropomorphic rabbit: cream-white fur, two long upright ears with pink inner "
     "surfaces, round black eyes, two front teeth, **wearing large black over-ear headphones "
     "and a soft grey home cardigan**, ")

CORRIDOR = ("**a narrow worn apartment corridor: chipped green painted walls, old floor tiles, "
            "a single bare bulb overhead, several closed doors** ")

SHOTS = {
 # ── 阿甘 ──
 "02_read": ([AGAN],
   "medium close shot in an old-town lane, " + A +
   "**holding his phone up and reading an order note, then tapping the screen and raising one "
   "hoof to his lips in a solemn hush gesture**, concentrating hard, "
   "warm afternoon light, brick wall behind, " + STYLE),

 "04_tiptoe": ([AGAN],
   "shot from behind and slightly to the side, " + A +
   "**tiptoeing down a narrow corridor, exaggeratedly careful, holding a small sealed paper "
   "takeaway bag in one hoof and his phone in the other, shoulders hunched**, "
   + CORRIDOR + "he is moving toward the right side of frame, " + STYLE),

 "05_bell": ([AGAN],
   "**extreme close-up, locked-off shot: a simple round doorbell button mounted on a door frame, "
   "and a grey three-fingered hoof hovering in front of it** — "
   "**there is a clearly visible gap of empty air between the hoof and the button, the hoof is "
   "NOT touching it, the button is dark and unlit**, the hoof slightly trembling, "
   "warm corridor light from the left, shallow depth of field, " + STYLE),

 "07_bag": ([AGAN],
   "low angle medium shot, " + A +
   "**kneeling and carefully setting a small paper takeaway bag down on the floor beside a "
   "closed apartment door, straightening it so it stands upright**, both hooves on the bag, "
   "the doorbell button visible on the door frame nearby but untouched, " + CORRIDOR + STYLE),

 "09_shock": ([AGAN],
   "**tight close-up of his face**, " + A +
   "**frozen mid-step, both ears sprung straight upright, eyes wide and staring toward the "
   "door, mouth slightly open in disbelief**, warm corridor light from one side, " + STYLE),

 "12_whisper": ([AGAN],
   "medium shot, " + A +
   "**crouched low beside the corridor wall, one hoof cupped near his mouth, whispering toward "
   "a closed door, body deliberately kept away from the doorbell**, anxious expression, "
   + CORRIDOR + STYLE),

 "15_evidence": ([AGAN],
   "two-part composition in one frame, " + A +
   "**on the left he holds up his phone showing a silent-mode screen, on the right his other "
   "hoof is held up in the air, plainly far away from the dark doorbell button**, "
   "**the gap between the hoof and the button is obvious**, earnest expression, " + STYLE),

 # ── 鹦鹉 ──
 "06_parrot_sees": ([PARROT],
   "medium close shot inside a warm apartment, " + P +
   "**perched on a wooden perch beside the entryway window, craning its neck and staring out "
   "through the glass at an orange silhouette outside, head cocked**, "
   "**at the very edge of its attention, its head turns briefly toward the door and the "
   "doorbell beside it**, blurred laptop and headphones in the background, warm room light, " + STYLE),

 "08_parrot_bell": ([PARROT],
   "medium close shot inside the same warm apartment, " + P +
   "**head thrown back, beak wide open mid-shout, chest puffed out proudly, wings slightly "
   "lifted**, on the same wooden perch beside the entryway window, "
   "**looking extremely pleased with itself as if it has just performed a perfect "
   "announcement**, warm room light, " + STYLE),

 "11_parrot_mimic": ([PARROT],
   "medium close shot on the same perch, " + P +
   "**leaning forward, beak open wide, one wing lifted for balance, bouncing once on the "
   "perch as it squawks**, body angled toward the doorway, "
   "an alert, eager expression — **not malicious, just delighted to be loud**, "
   "warm room light, " + STYLE),

 "13_parrot_loud": ([PARROT],
   "close shot on the same perch, " + P +
   "**both wings spread wide open, beak open as far as it goes, chest fully puffed, "
   "the feathers on its crest standing straight up**, at maximum volume, "
   "warm room light from behind, " + STYLE),

 # ── 兔子 ──
 "10_rabbit_call": ([RABBIT],
   "medium shot inside a warm small apartment, " + R +
   "**sitting at a small desk in front of a laptop, in the middle of a video meeting, one paw "
   "raised with a single finger pressed to its lips, the other pointing urgently toward the "
   "window where the parrot sits**, worried not angry, "
   "a simple blurred laptop screen with no readable text, warm lamp light, " + STYLE),

 "17_fivestar": ([RABBIT],
   "medium close shot at a doorway, " + R +
   "**holding a phone with one paw and tapping the screen, then giving a small apologetic "
   "thumbs-up toward the corridor**, relieved and sheepish, "
   "a phone screen showing five filled stars, warm interior light, " + STYLE),

 # ── 双人 ──
 "14_door_open": ([AGAN, RABBIT],
   "**medium two-shot at an open apartment door**, "
   "**Agan stands on frame LEFT, outside in the dim corridor, two steps back from the door**; "
   "**the rabbit stands on frame RIGHT, inside the doorway, still wearing its headphones**, "
   "the door **swings inward into the room**, a small paper bag stands upright on the floor "
   "between them, " + A + "and " + R +
   "warm interior light spilling out against the cool corridor, " + STYLE),

 # ── 三人（如果多图失败会退化）──
 "16_triangle": ([AGAN, RABBIT],
   "**three-subject composition through an open doorway**: the rabbit stands in the doorway on "
   "frame RIGHT turned to look back over its shoulder, " + R +
   "and **the parrot is perched on a wooden perch just inside the room beside the doorway, "
   "chest puffed and beak open mid-shout**; " + A +
   "stands on frame LEFT outside in the corridor, turning his head toward the bird, "
   "warm interior light, cool corridor, " + STYLE),

 # ── 门缝（不传参考！）──
 "18_neighbors": ([],
   "**wide corridor shot, no main character**, " + CORRIDOR +
   "**one apartment door on the left has just opened a narrow crack, warm light spilling out "
   "through the gap, and a single pair of round animal eyes peeking out through the crack**; "
   "the eyes are looking **down at the floor outside its own door**, where there is nothing — "
   "**the expression is first expectant, then deflating into confusion**; "
   "empty corridor beyond, single bare bulb, " + STYLE),
}

if __name__ == "__main__":
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    ok, fail = 0, []
    for i, (name, (refs, prompt)) in enumerate(SHOTS.items(), 1):
        if only and not any(o in name for o in only):
            continue
        out = os.path.join(EP, name + ".png")
        if os.path.exists(out) and os.path.getsize(out) > 200000:
            print(f"  · [{i}/{len(SHOTS)}] {name} 已存在", flush=True)
            ok += 1
            continue
        tag = "无参考" if not refs else ("+".join(os.path.basename(r)[:6] for r in refs))
        print(f"  → [{i}/{len(SHOTS)}] {name}  [{tag}] ...", flush=True)
        try:
            t0 = time.time()
            kw = dict(size="2K", ratio="16:9", save_to=out)
            if refs:
                kw["init_images"] = [r for r in refs if os.path.exists(r)]
            agnes.gen_image(prompt, **kw)
            dt = time.time() - t0
            with open(os.path.splitext(out)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
                json.dump({"prompt": prompt,
                           "refs": [os.path.basename(r) for r in refs],
                           "elapsed_s": round(dt, 1)}, f, ensure_ascii=False, indent=2)
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
            ok += 1
        except Exception as e:
            print(f"    ✗ {str(e)[:150]}", flush=True)
            fail.append(name)
    print(f"\n完成 {ok}/{len(SHOTS)}" + (f"，失败：{fail}" if fail else ""), flush=True)
