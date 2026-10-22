#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
风格探索 v9 —— 赛博朋克 + 我推荐的三个替代方向

先说判断：
  用户要"赛博朋克"。它和本片的契合点是**天然的**——
    · 赛博朋克的核心就是「高科技、低生活」的底层劳动者
    · 外卖骑手是赛博朋克世界最典型的职业（《银翼杀手》的雨夜 + 《赛博朋克2077》的配送）
  但它和立项书的两条硬设定**直接冲突**：
    · 立项书写"美式卡通复古风、暖褐色调、治愈解压、明确拒绝负能量"
    · 赛博朋克是冷色/霓虹/压抑/雨夜/反乌托邦

  所以本批出四种，让用户看实际效果再定：
    C1 纯赛博朋克     —— 霓虹冷调、雨夜、全息广告，最冲击但最压抑
    C2 暖赛博朋克     —— 保留暖褐底，只加黄/青霓虹点缀 + 科技配件（**折中，我最推荐**）
    C3 Solarpunk 太阳朋克 —— 赛博朋克的反面：高科技但明亮、绿色、乐观、社区互助
                            （**和"治愈解压"最配，而且同样有科幻感**）
    C4 复古未来主义    —— 70-80 年代科幻海报的想象，和"美式卡通复古"最同源

  四张都保持同一套角色识别点：驴脸 / 立耳 / 帽 / 领带 / 背心 / 叉腰姿态。
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

# ★ 角色骨架（四种风格共用，保证是同一个角色）
CHAR = ("an anthropomorphic hinny delivery rider — a horse's compact body with a donkey's "
        "long straight face — lean and wiry, standing upright on two legs, "
        "**weight on one leg with the other knee softly bent, one hand on his hip**, "
        "**his body flows along one single S-curve, nothing stiff**, "
        "two long ears standing up with the left one bent over at the tip, "
        "a short mane lying flat along the neck, "
        "**a battered baseball cap**, "
        "**a loud second-hand necktie over a plain undershirt**, "
        "one hand raised holding a delivery bag, "
        "a confident crooked half-smile, kind eyes with clear catchlights, "
        "arms end in three-fingered hoof-hands, ")

STYLES = {
 # ── C1 纯赛博朋克 ──
 "C1": CHAR + (
   "**CYBERPUNK**: neon-drenched rainy night street, glowing magenta and cyan holographic "
   "signs reflected in puddles, dense vertical city, cables and pipes overhead, "
   "his undershirt has thin glowing circuit trim, the delivery bag glows faintly, "
   "cold blue-teal shadows with hot pink rim light, "
   "cinematic cyberpunk anime illustration, bold clean outlines, "
   "high contrast, volumetric neon haze, "),

 # ── C2 暖赛博朋克（折中，推荐）──
 "C2": CHAR + (
   "**WARM CYBERPUNK**: the same warm sepia world as a retro cartoon, but wired — "
   "mustard-yellow and cyan neon strips glow along the edges of his cap and bag, "
   "a thin glowing seam on his tie, faint holographic price tags floating near his ear, "
   "warm brown and amber base palette with two neon accent colors only, "
   "**optimistic and cosy rather than oppressive**, soft evening light, "
   "retro cartoon illustration with thick wobbly black outlines, flat colors, "
   "halftone dots, "),

 # ── C3 Solarpunk（和"治愈"最配）──
 "C3": CHAR + (
   "**SOLARPUNK**: a bright sunlit street of the future, "
   "solar panels and living green vines growing over white ceramic architecture, "
   "small wind turbines on rooftops, hanging plants and glass, "
   "his cap has a tiny solar panel patch, his bag is woven from recycled bioplastic, "
   "**warm golden light, fresh greens and cream whites, hopeful and clean**, "
   "no grime, no darkness, "
   "art nouveau influenced retro cartoon, thick clean outlines, flat colors, "
   "gentle halftone texture, "),

 # ── C4 复古未来主义 ──
 "C4": CHAR + (
   "**RETRO-FUTURISM of the 1970s**: a vision of tomorrow painted in 1978, "
   "chunky cream-and-orange plastic machinery, bubble-shaped vehicles, "
   "concentric ring towers, "
   "his cap has a chrome buckle, his bag is a hard-shell pod with rounded corners, "
   "**burnt orange, avocado green and cream, warm airbrushed gradients, "
   "grainy print texture**, "
   "vintage sci-fi poster illustration, bold confident outlines, "),
}

if __name__ == "__main__":
    ok = 0
    for tag, prompt in STYLES.items():
        out = os.path.join(BATCH, f"STYLE_{tag}.png")
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
