#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
阿甘定妆 v6 —— 修「没有美感」

用户：「你这个设计一点美感也没有啊」

诊断（Q4 为什么丑，逐条对上了查到的 "Appeal Killers"）：
  ① 没有动作线（Line of Action）
     → "If you ignore this, your characters will look like they have a wooden plank taped to their spine."
     **Q4 就是脊柱上贴了块木板。**
  ② 平行曲线
     → "Never use two parallel curves. Two identical outward curves looks like a sausage."
     **Q4 的手臂就是两根香肠。**
  ③ 负空间消失
     → "Amateurs keep limbs too close to the torso — this creates a blob silhouette.
        Pros spend more time on the NEGATIVE SPACE, the gaps between arms and legs."
     **Q4 手臂贴着箱体，糊成一坨。**
  ④ 镜像对称
     → "Symmetry is the death of appeal... It looks like a robot."
        "Never draw a character looking dead-on at the camera."
     **Q1/Q2 正面正对，像护照照片。**
  ⑤ 细节过载
     → "Every line is a chance for confusion. Scratchy detail looks hairy and cheap."
     **Q4 的缝线+胶带+补丁全是碎线。**
  ⑥ 色彩无层级
     → "One dominant colour... then one or two accents. Bright saturated everywhere = visual noise."
     **Q4 亮黄大块和棕色身体两个都强。**

本轮把六条修正**全部写进 prompt**：
  · 一条贯穿全身的 S 曲线动作线
  · 躯干改成**圆角梯形**（不是正方形），一侧鼓起、整体微歪
  · 手臂**离开躯干**，留出负空间
  · **一条边直线 + 一条边曲线**（制造张力，不做平行曲线）
  · 3/4 侧角 + 头微倾 + 一肩高一肩低 + 重心在一条腿（contrapposto）
  · **只留一处修补**，其余干净
  · 降饱和，箱体只比毛色略强一点

四个变体：箱式程度递减，看"能不能既记住又好看"。
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATCH = os.path.join(ROOT, "work", "char", time.strftime("batch_%Y%m%d_%H%M"))
os.makedirs(BATCH, exist_ok=True)

STYLE = ("american retro cartoon style, thick wobbly black ink outlines with VARIED line weight "
         "(heavy on the outer silhouette, thin inside), flat solid colors, "
         "visible halftone dot texture, warm sepia palette, nostalgic picture-book mood")

# ★ 动作线（最重要的修正）
LINE_OF_ACTION = ("**the whole body flows along one single S-curve**: it starts at the soft arc of his "
                  "bent neck, sweeps down through a torso that leans a few degrees off vertical, "
                  "and finishes in legs that curve back the other way. "
                  "Nothing in the pose is stiff or plank-straight. ")

# ★ 不对称 + 负空间
ASYMMETRY = ("**he is seen from a three-quarter angle, not straight on**, head tilted slightly to "
             "one side, one shoulder higher than the other, standing with his weight on one leg "
             "while the other knee is softly bent, "
             "**both arms hang clear of the body with visible empty gaps between arm and torso**, "
             "each arm has one straight edge and one curved edge so it never reads as a sausage, ")

MULE = ("a long narrow donkey face with a straight profile, a gentle closed-mouth smile, "
        "two long ears standing up, the LEFT one bent over at its tip, "
        "a short mane in one narrow strip lying flat along the neck, "
        "warm chestnut-brown fur with a lighter muzzle, ")

CLEAN = ("clean simple surfaces, **only one visible repair**: a single short line of stitching "
         "across one corner, nothing else added, ")

VARIANTS = {
 # R1：圆角梯形箱 —— 主推
 "R1": "character design, plain warm cream background, " + LINE_OF_ACTION +
       "**his torso is a rounded trapezoid parcel-box shape** — narrower at the bottom, "
       "with softly convex bulging sides that catch the light, one corner folded up slightly, "
       "the box reads as a soft living volume rather than a rigid cube, " +
       ASYMMETRY + MULE +
       "arms end in three-fingered hoof-hands, one hand raised holding a small paper bag, " +
       CLEAN +
       "**muted warm ochre box, only slightly more saturated than his chestnut fur**, "
       "no clothing, " + STYLE,

 # R2：桶形 —— 更柔和的版本
 "R2": "character design, plain warm cream background, " + LINE_OF_ACTION +
       "**his torso is a soft barrel shape with rounded shoulders and a gently tapering "
       "bottom, like a canvas delivery bag that has settled into a comfortable volume**, " +
       ASYMMETRY + MULE +
       "arms end in three-fingered hoof-hands, one hand raised holding a small paper bag, " +
       CLEAN +
       "**muted warm sand and chestnut palette**, no clothing, " + STYLE,

 # R3：背篓 —— 完全保留动物身体，只加一个道具（最保守）
 "R3": "character design, plain warm cream background, " + LINE_OF_ACTION +
       "**a slim anthropomorphic mule with a small woven delivery basket strapped on his back**, "
       "his own narrow chest and belly visible in front of the basket, " +
       ASYMMETRY + MULE +
       "arms end in three-fingered hoof-hands, one hand raised holding a small paper bag, " +
       CLEAN +
       "**muted chestnut fur with a warm ochre basket**, no clothing, " + STYLE,

 # R4：R1 的加强版 —— 箱体更有"生命感"（鼓起、变形）
 "R4": "character design, plain warm cream background, " + LINE_OF_ACTION +
       "**his torso is a soft squarish parcel form that has been squeezed by life** — "
       "one side bulges out, the opposite corner is dented in, the bottom sags slightly, "
       "so it reads as a warm living lump rather than geometry, " +
       ASYMMETRY + MULE +
       "arms end in three-fingered hoof-hands, one hand raised holding a small paper bag, " +
       CLEAN +
       "**muted warm ochre and chestnut palette**, no clothing, " + STYLE,
}

if __name__ == "__main__":
    ok = 0
    for tag, prompt in VARIANTS.items():
        out = os.path.join(BATCH, f"AGAN_{tag}.png")
        try:
            t0 = time.time()
            paths = agnes.gen_image(prompt, size="2K", ratio="3:4", save_to=out)
            dt = time.time() - t0
            for p in paths:
                with open(os.path.splitext(p)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
                    f.write(json.dumps({"tag": tag, "prompt": prompt,
                                        "size": "2K", "ratio": "3:4",
                                        "model": agnes.IMG_MODEL,
                                        "elapsed_s": round(dt, 1)}, ensure_ascii=False, indent=2))
                print(f"  ✓ {os.path.basename(p)}  {dt:.0f}s")
                ok += 1
        except Exception as e:
            print(f"  ✗ {tag}: {str(e)[:160]}")
    print(f"\n共 {ok} 张 → {BATCH}")
