#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
第一集 · 分镜首帧生成（含角色一致性控制）
=====================================

分镜来源：Gemini 的 `Luoma_Agan_Episode_01_Storyboard.md`（7 镜 / 28.6s）

一致性策略（关键）：
  角色还没定，但 7 个镜头如果各报各的 prompt，会出 7 个不同的阿甘。
  所以：
    第 0 步：先生成一张【角色标准照】
    第 1 步：用这张做 I2I 参考，生成 7 张分镜首帧
  Agnes 图生图输入走 `extra_body.image`（已验证）。

角色锚点（从我们几轮实验里收敛出来的）：
  · 驴骡：长直脸 + 中等长立耳（用马讲身体、用驴讲脸，避免漂成纯驴）
  · 栗棕色毛，比马小、比驴大
  · 左耳缠一圈褪色黄胶带（记忆点）
  · 反戴黄色棒球帽 + 二手花领带 + 旧米色背心
  · 瘦小、S 曲线前倾、三指蹄手
  · 美式卡通复古：粗抖黑描边 + 平涂 + 网点 + 暖褐
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01")
os.makedirs(EP, exist_ok=True)

STYLE = ("retro american cartoon style, thick wobbly black ink outlines with varied line weight, "
         "flat solid colors, visible halftone dot texture, warm sepia palette, "
         "nostalgic picture-book mood")

CHAR = ("an anthropomorphic hinny delivery rider — a horse's compact body with a donkey's long "
        "straight face — lean and wiry, warm chestnut-brown fur, "
        "a battered mustard-yellow baseball cap worn backwards, "
        "a loud second-hand necktie over a plain cream undershirt, "
        "**a band of faded yellow cloth tape wrapped around his left ear**, "
        "two medium-length ears standing up, a short flat mane along the neck, "
        "arms end in three-fingered hoof-hands, kind eyes with clear catchlights, ")

# ── 第 0 步：角色标准照 ──
SHEET = ("character reference sheet, front view standing portrait, plain warm cream background, "
         + CHAR +
         "standing upright on two legs with weight on one leg, slightly leaning forward "
         "as if always in a hurry, a confident crooked half-smile, "
         "clean simple surfaces, full body visible, " + STYLE)

# ── 第 1 步：7 个分镜首帧（共用同一角色参考）──
SHOTS = {
 "S1_alley_dawn": (
   "high angle wide establishing shot, a dense old-town alley at dawn, "
   "**many laundry poles with drying clothes strung between handshake buildings**, "
   "warm morning sunlight slicing across old brick walls, two sparrows on a wire above, "
   "no people, empty quiet street, " + STYLE),

 "S2_mirror_cap": (
   "medium shot, inside a tiny rented room, " + CHAR +
   "standing before a cracked old mirror, pressing his backwards baseball cap onto his head, "
   "the mirror shows the yellow tape on his left ear, a confident lopsided grin, "
   "warm lamp light, cramped cosy interior, " + STYLE),

 "S3_scooter": (
   "side tracking action shot, " + CHAR +
   "riding a small yellow electric scooter through an old alley, "
   "**lifting a steaming insulated delivery box high overhead onto the rear rack**, "
   "a small paper pinwheel tied to the handlebar, "
   "**his lean body leaning forward in a clean S-curve**, ears blown back by the wind, "
   "the mane at the back of his neck lifting, motion blur on the background, " + STYLE),

 "S4_bridge": (
   "dramatic low angle dynamic shot, " + CHAR +
   "leaning low on his yellow scooter, leaning into a tight turn across a narrow vintage "
   "iron bridge with a gap in the planks, a huge rhino freight truck coming the other way, "
   "**the delivery box on the back perfectly level, not a drop spilled**, "
   "river glittering below, morning glare, " + STYLE),

 "S5_lobby": (
   "wide interior shot, " + CHAR +
   "small in frame, standing before towering glass security turnstiles inside a sleek "
   "corporate skyscraper lobby, a stern big dog security guard pointing at a sign, "
   "cold teal and grey lighting, **the tiny courier dwarfed by the architecture**, " + STYLE),

 "S6_elevator": (
   "tight enclosed elevator shot, " + CHAR +
   "seen in the bronze mirror walls, **his thin shoulders slightly trembling**, "
   "taking a deep breath, both hands straightening his necktie, "
   "pulling the corners of his mouth up into a bright determined smile, "
   "warm amber light on metal, tender and quiet, " + STYLE),

 "S7_rooftop": (
   "epic panoramic shot from a high rooftop terrace, " + CHAR +
   "seen from behind at the railing, eating a small bread roll, "
   "**a vast sprawling sunlit fictional metropolis spreads out below, "
   "old dense low town in warm orange merging into cool blue glass towers**, "
   "golden sunrise rim light, deeply emotional and hopeful, " + STYLE),
}

if __name__ == "__main__":
    log = {}

    # 第 0 步
    sheet_p = os.path.join(EP, "S0_character_sheet.png")
    if not os.path.exists(sheet_p):
        print("[0] 角色标准照 ...")
        agnes.gen_image(SHEET, size="2K", ratio="3:4", save_to=sheet_p)
        with open(os.path.splitext(sheet_p)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
            json.dump({"prompt": SHEET, "size": "2K", "ratio": "3:4"}, f,
                      ensure_ascii=False, indent=2)
        print(f"  ✓ {os.path.basename(sheet_p)}")

    # 第 1 步：逐镜出首帧，全部带角色参考
    for i, (name, prompt) in enumerate(SHOTS.items(), start=1):
        out = os.path.join(EP, f"{name}.png")
        if os.path.exists(out):
            print(f"[{i}] {name} 已存在，跳过")
            log[name] = out
            continue
        print(f"[{i}] {name} ...")
        try:
            t0 = time.time()
            agnes.gen_image(prompt, size="2K", ratio="16:9",
                            init_images=[sheet_p], save_to=out)
            dt = time.time() - t0
            with open(os.path.splitext(out)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
                json.dump({"prompt": prompt, "init_image": "S0_character_sheet.png",
                           "size": "2K", "ratio": "16:9", "elapsed_s": round(dt, 1)},
                          f, ensure_ascii=False, indent=2)
            log[name] = out
            print(f"  ✓ {dt:.0f}s")
        except Exception as e:
            print(f"  ✗ {str(e)[:180]}")

    print(f"\n共 {len(log)} 张 → {EP}")
