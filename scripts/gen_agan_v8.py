#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
阿甘定妆 v8 —— 按用户的直觉做「造型」，而不是继续磨「裸角色」

用户：「不好看，不吸引人，没有特点……要不打个领带，做个帅气的发型」

查证支持（《疯狂动物城》）：
  "每一个动物都会有属于自己特定的**发型**，从发型中会传达很多信息——
   性别、年龄和身份都能通过他们的发型体现出来。"
  "**服装也是能够传达动物内心的活动变化**。"
  "又帅又萌是穿搭重点" —— 狐狸尼克 = 印花衬衫 × 领带 = 吊儿郎当的街头风

**关键修正：我一直在磨"裸角色"，但裸角色没有戏剧性，看不出性格。
  造型（发型+服装+配件）才是人格的载体。**

阿甘的"帅"应该是什么？
  他不是精英，是瘦小的底层骑手。他的帅只能是 **「穷讲究」**：
    · 帽子破了边、领带是捡来的，但系得一丝不苟
    · 衣服旧，但干净、利落
    · 精气神不能塌 —— "知道生活很难但选择笑着扛"

四个造型方案（发型的三种解法 + 帽子的四种用法）：
  T1 压檐鸭舌帽 + 旧领带        —— 帽子压住一只眼，神秘感 + 帅
  T2 压檐鸭舌帽 + 领带 + 背篓    —— 完整职业形象
  T3 不戴帽，鬃毛吹成"飞机头"    —— 用鬃毛做发型（最忠于动物本体）
  T4 帽子反戴 + 领带 + 耳机线    —— 最街头

共同保留：**左耳缠黄胶带**（前一轮验证有效的记忆点）
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

STYLE = ("american retro cartoon style, thick wobbly black ink outlines with varied line weight, "
         "flat solid colors, visible halftone dot texture, warm sepia palette, "
         "nostalgic picture-book mood")

LOA = ("**the whole body flows along one single S-curve**, torso leaning a few degrees off "
       "vertical, weight on one leg with the other knee softly bent, "
       "**arms hang clear of the body leaving visible gaps**, ")

# ★ 物种锚（反驴漂移）
MULE = ("**a hinny — the child of a horse father and a donkey mother — "
        "so he has a horse's compact body and a donkey's long straight face**, "
        "lean wiry frame with long thin legs and a narrow waist, "
        "warm chestnut-brown fur with a lighter muzzle, ")

# ★ 造型：穷讲究
CAP = ("**a battered old baseball cap worn low so the brim shadows one eye**, "
       "the fabric faded and frayed at the edge, the brim slightly bent, ")

TIE = ("**a narrow vintage necktie in a loud clashing pattern, clearly second-hand**, "
       "tied neat and precise as if it matters to him, "
       "worn over a plain worn-out undershirt, ")

EAR_TAPE = ("**a band of faded yellow cloth tape wrapped around the middle of his LEFT ear**, "
            "wound a few times, the edges curling, ")

POMP = ("**his mane is styled into a small swept-up pompadour on top of his head**, "
        "combed back and up with a bit of cheap pomade, a single lock falling loose over the brow, ")

VARIANTS = {
 "T1": "character design, plain warm cream background, " + LOA +
       CAP + TIE + EAR_TAPE + MULE +
       "a confident crooked half-smile, kind eyes with clear catchlights, "
       "arms end in three-fingered hoof-hands, clean simple surfaces, " + STYLE,

 "T2": "full body character design, plain warm cream background, " + LOA +
       CAP + TIE + EAR_TAPE + MULE +
       "**a small woven delivery basket strapped on his back**, "
       "a confident crooked half-smile, arms end in three-fingered hoof-hands, "
       "clean simple surfaces, " + STYLE,

 "T3": "character design, plain warm cream background, " + LOA +
       POMP + TIE + EAR_TAPE + MULE +
       "**no hat, the hairstyle does the work**, "
       "a confident crooked half-smile, arms end in three-fingered hoof-hands, "
       "clean simple surfaces, " + STYLE,

 "T4": "character design, plain warm cream background, " + LOA +
       "**his baseball cap is worn backwards**, the strap showing, " +
       TIE + EAR_TAPE +
       "**one thin earphone cord hanging loose around his neck**, " + MULE +
       "a confident crooked half-smile, arms end in three-fingered hoof-hands, "
       "clean simple surfaces, " + STYLE,
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
