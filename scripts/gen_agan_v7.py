#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
阿甘定妆 v7 —— 记忆点从「改造身体」改成「一个配件」

判断修正（v6 之后才想明白）：
  我前面押的赌注是「把外卖箱变成身体」。回看经典角色，**没有一个这样做**：
    · 海绵宝宝是方的 —— 因为海绵本来就是方的
    · 米老鼠三个圆 —— 因为老鼠本来就是圆的
    · 《史莱克》的驴 —— 靠表情和性格，不靠造型
    · 维尼的 Eeyore —— 靠【尾巴上的粉蝴蝶结】，一个配件
    · 爆笑虫子 —— 靠两只虫子的粗细对比，不靠道具
  **"把职业道具变成身体"太概念化，像标志不像角色，而且必然牺牲美感。**

新方向：
  主体沿用 R3 的架子（S 曲线 + 3/4 侧角 + 拟人 + 背篓，美感最好）
  **记忆点 = 左耳上永久缠着一圈褪色的黄色布胶带**

  这一个配件同时解决四件事：
    ① **视觉记忆点**：形状（耳朵上一个环）+ 颜色（黄），剪影上就是一处异样
    ② **讲人物**：穷，自己拿胶带补的，"知道生活很难但选择笑着扛"
    ③ **有美感**：是生活痕迹，不是几何改造，不破坏形体
    ④ **绕开"缺角画不出来"**：不用画缺角，画"用胶带缠着的耳朵"，故事反而更狠
    ⑤ 黄色只在小面积，不跟毛色打架（解决了 Q4 的色彩冲突）

四个变体：
  S1 胶带缠耳（主推）
  S2 胶带缠耳 + 背篓 + 更瘦
  S3 胶带 + 耳朵一高一低（双重记忆点）
  S4 胶带 + 脖子上挂配送单夹
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

# 动作线（v6 验证有效，美感主要来源）
LOA = ("**the whole body flows along one single S-curve**: from the soft arc of his bent neck, "
       "down through a torso leaning a few degrees off vertical, ending in legs curving back "
       "the other way, nothing stiff or plank-straight, ")

ASYM = ("seen from a three-quarter angle, head tilted a little to one side, one shoulder higher "
        "than the other, weight on one leg with the other knee softly bent, "
        "**arms hang clear of the body leaving visible gaps**, "
        "each arm has one straight edge and one curved edge, ")

# ★ 反驴漂移（v3 验证有效）
MULE = ("a long narrow donkey face with a straight profile, "
        "a short mane in one narrow strip lying flat along the neck, "
        "a short thin tail whose upper half is bare and whose tip carries one small tuft, "
        "lean wiry body with thin legs, warm chestnut-brown fur, lighter muzzle, ")

# ★ 核心记忆点
TAPE = ("**THE SIGNATURE DETAIL: a band of faded yellow cloth tape is wrapped around the middle "
        "of his LEFT ear**, wound two or three times, the tape edges curling and slightly dirty, "
        "the ear above the tape bends over a little under its weight, "
        "this taped ear is the one thing that makes him instantly recognisable, ")

GENTLE = ("a gentle closed-mouth smile, kind eyes with clear catchlights, "
          "arms end in three-fingered hoof-hands, ")

CLEAN = ("clean simple surfaces, nothing else added, no clutter, ")

VARIANTS = {
 "S1": "character design, plain warm cream background, " + LOA +
       TAPE + ASYM + MULE + GENTLE +
       "one hand raised holding a small paper bag, " + CLEAN + STYLE,

 "S2": "full body character design, plain warm cream background, " + LOA +
       TAPE + ASYM + MULE +
       "**a small woven delivery basket strapped on his back**, "
       "his own narrow chest visible in front of it, " + GENTLE +
       "one hand raised holding a small paper bag, " + CLEAN + STYLE,

 "S3": "character design, plain warm cream background, " + LOA +
       "**his two ears are different heights — the right one stands tall and the left one is "
       "shorter and wrapped in a band of faded yellow cloth tape**, " +
       ASYM + MULE + GENTLE +
       "one hand raised holding a small paper bag, " + CLEAN + STYLE,

 "S4": "full body character design, plain warm cream background, " + LOA +
       TAPE + ASYM + MULE +
       "**a small clipboard with delivery slips hangs from a cord around his neck**, "
       + GENTLE + "one hand raised holding a small paper bag, " + CLEAN + STYLE,
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
