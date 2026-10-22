#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
S2 单镜修复 —— 推镜诊断失败后的第三版尝试

实测轨迹：
  v1  "he pushes the cap down..."（运镜写在最后）      → 拉远 zoom=-0.18
  v2  "THE CAMERA DOLLIES IN ... never pulls back"    → 还是拉远 zoom=-0.46
  v3  本脚本：**换成"光学变焦"语言 + 分阶段描述**

判断：封闭空间 + 人物占满画面时，模型分不清"相机前移"和"人物前移"，
     干脆退化成缓慢拉远。所以改用 **zoom（焦距变化）** 而不是 dolly（位移）。

三个变体，各出一次，选运动最接近推镜的：
  Z1 光学变焦（zoom in / telephoto）
  Z2 画面占比变化（head 从 1/3 长到 2/3）
  Z3 干脆固定机位（保底方案，绝不错）
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01")
OUTDIR = os.path.join(EP, "clips_v2")
os.makedirs(OUTDIR, exist_ok=True)
IMG = os.path.join(EP, "S2_mirror_cap.png")

ACT = ("Meanwhile he pushes the backwards cap down onto his head with both hands, "
       "then gives a lopsided confident grin and a tiny nod. The lamp behind him flickers softly.")

VARIANTS = {
 "Z1": ("**THE LENS ZOOMS IN — a pure OPTICAL zoom, telephoto becoming longer.** "
        "His head and shoulders grow steadily larger until they fill most of the frame. "
        "The room behind him compresses, its walls spreading wider and blurring at the edges. "
        "This is a zoom, not a camera move: the viewpoint does not travel, "
        "the focal length simply tightens. Nothing ever zooms out. " + ACT),

 "Z2": ("**He grows from one third to two thirds of the frame height over the shot.** "
        "The camera frame closes in on his face; the mirror and the room shrink toward the "
        "outer edges and then pass out of frame entirely. "
        "The composition tightens progressively from a medium shot to a close-up. "
        "It only ever tightens, never widens. " + ACT),

 "Z3": ("**THE CAMERA IS LOCKED ON A TRIPOD AND DOES NOT MOVE AT ALL** — "
        "no zoom, no push, no pan, the frame is completely fixed for the whole shot. "
        "Only he moves inside the still frame. " + ACT),
}

if __name__ == "__main__":
    for tag, motion in VARIANTS.items():
        out = os.path.join(OUTDIR, f"S2_mirror_cap_{tag}.mp4")
        if os.path.exists(out) and os.path.getsize(out) > 60000:
            print(f"  · {tag} 已存在")
            continue
        print(f"  → {tag} ...", flush=True)
        try:
            t0 = time.time()
            agnes.gen_video(motion, seconds="4", mode="keyframe",
                            images=[IMG], ratio="16:9", save_to=out)
            dt = time.time() - t0
            with open(out + ".motion.txt", "w", encoding="utf-8") as f:
                json.dump({"tag": tag, "motion": motion}, f, ensure_ascii=False, indent=2)
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
        except Exception as e:
            print(f"    ✗ {str(e)[:160]}")
    print("done")
