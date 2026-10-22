#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP01《第一万单》· 26 个实拍镜头首帧

⛔ 上一版"故事说不清"的根因，在分镜层面已修（见 story/EP01_第一万单.md）：
   · S01 手机屏幕先交代"他是骑手、9996 单" → 身份
   · 三单重复（蛋糕 / 花 / 玩具），每单都拍"取—送—别人的反应" → 形成"他一直在送别人的生日"
   · 9996→9997→9999→10000 四镜递进 → 有仪式感
   · 等红灯 / 擦汗 / 楼道听笑声 → 劳动者的体感

⚠️ 4 个手机屏幕镜头（S01/S04/S20/S22）**不在这里**——
   AI 生成中文必然乱码，那几镜用 PIL 程序化渲染（render_phone.py）。

角色一致性：全部传同一张用户定稿图做 I2I 参考，但**没有任何空镜**（26 镜全部有角色或人物反应）。
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01c")
os.makedirs(EP, exist_ok=True)
HERO = os.path.join(ROOT, "assets", "hero", "AGAN_MASTER_2k.png")

STYLE = ("vintage American cartoon style, thick bold black ink outlines, "
         "flat solid colors, visible halftone dot texture, "
         "warm nostalgic picture-book mood, cinematic 16:9 composition")

HERO_DESC = ("**a small cartoon hinny delivery courier** — "
             "**slate blue-grey fur**, **a cream-white squarish muzzle** with two black oval "
             "nostrils on its top, **very large round eyes** with big white sclera, black pupils "
             "and white catchlights, **two long upright ears** with pale grey inner surfaces, "
             "a simple thin curved line as a smile, **an amber-orange zipped vest**, "
             "**an orange backpack**, slate-grey three-fingered hands, black hooves, "
             "a thin tail with a black tuft at the tip, ")

HERO_SHORT = ("**the same slate blue-grey hinny courier with the cream muzzle, huge round eyes, "
              "long ears and amber-orange vest** ")

SHOTS = {
 # ── 第一幕 ──
 "S02_bed": dict(ref=True,
   prompt="medium shot, inside a tiny rented room at dawn, " + HERO_DESC +
          "sitting on the edge of a narrow bed, pulling on his amber vest, "
          "**a small homemade paper flag in one hand ready to pin on his cap**, "
          "a kettle and a cracked mirror behind him, one warm shaft of light across the wall, "
          "poor but tidy, " + STYLE),

 "S03_mirror": dict(ref=True,
   prompt="medium close shot, " + HERO_DESC +
          "standing before a cracked mirror with the paper flag now pinned to his cap, "
          "**breaking into a slightly goofy wide grin at his own reflection**, "
          "the reflection smiles even wider, warm lamp light from one side, " + STYLE),

 "S05_door": dict(ref=True,
   prompt="wide shot from behind and slightly low, " + HERO_SHORT +
          "**stepping out through an open doorway into a bright corridor** with laundry "
          "hanging overhead, strong morning sunlight from outside, "
          "his silhouette against the light, the dark room behind him, " + STYLE),

 "S06_ride": dict(ref=True,
   prompt="dynamic wide shot, " + HERO_DESC +
          "riding a small yellow electric scooter fast down an old-town alley toward the viewer, "
          "**ears blown back, backpack straps flapping**, old brick walls and hanging laundry "
          "rushing past on both sides, morning glare and long shadows, " + STYLE),

 "S07_redlight": dict(ref=True,
   prompt="medium shot, " + HERO_SHORT +
          "**stopped at a red pedestrian light on his scooter, one foot on the ground**, "
          "looking up at the sky, chest rising as he catches his breath, "
          "other scooters waiting around him, morning city light, " + STYLE),

 "S08_wipe": dict(ref=True,
   prompt="close medium shot, " + HERO_SHORT +
          "**wiping his forehead with the back of one hand**, his cap slightly askew, "
          "a tired but content expression, thin sweat line on his temple, "
          "street background softly blurred, " + STYLE),

 # ── 第二幕 · 第一单（蛋糕）──
 "S09_cakeshop": dict(ref=True,
   prompt="medium shot at a bakery counter, " + HERO_SHORT +
          "**receiving a white cake box tied with a ribbon through the service window**, "
          "a baker's hands pushing it out to him, warm bakery light, "
          "pastry trays and a small cake display behind, " + STYLE),

 "S10_carry": dict(ref=True,
   prompt="side tracking shot, " + HERO_SHORT +
          "riding one-handed on his scooter, **the other arm carefully cradling a white cake box "
          "against his chest**, leaning slightly to protect it, "
          "street sliding past, afternoon light, " + STYLE),

 "S11_deliver1": dict(ref=True,
   prompt="shot through an open apartment door, " + HERO_SHORT +
          "seen from behind at the left edge handing over the cake box, "
          "**inside a warm bright flat a whole family gathers around, a small child jumping up "
          "with both arms raised shouting with joy**, balloons and paper garlands, "
          "warm orange light flooding out into the dim corridor, " + STYLE),

 "S12_turn": dict(ref=True,
   prompt="medium wide shot, " + HERO_SHORT +
          "**standing alone in a dim apartment corridor, the door now shut behind him, "
          "body half turned away, mid-step, looking back over his shoulder once**, "
          "empty hands, single overhead bulb, long shadow on the floor, " + STYLE),

 # ── 第二幕 · 第二单（花）──
 "S13_flowershop": dict(ref=True,
   prompt="medium shot at a small flower shop, " + HERO_SHORT +
          "**receiving a big bunch of red roses wrapped in paper**, the florist's hands passing "
          "it across, buckets of flowers and green leaves all around, soft afternoon light, " + STYLE),

 "S14_blocked": dict(ref=True,
   prompt="wide low angle shot, " + HERO_SHORT +
          "**small in frame in a tall cold glass office lobby, a big stern dog security guard in "
          "uniform raising one hand to stop him** and pointing at a sign, "
          "polished floor reflections, cold teal-grey light, he holds the roses carefully, " + STYLE),

 "S15_deliver2": dict(ref=True,
   prompt="medium shot in an office corridor, " + HERO_SHORT +
          "**handing the bunch of red roses to a young man in a shirt**, the man taking them "
          "with both hands, nervous happy grin, glass office walls, cool daylight, " + STYLE),

 "S16_stiff": dict(ref=True,
   prompt="close medium shot, " + HERO_SHORT +
          "**nodding with a slightly stiff smile, one hand still raised in a small wave**, "
          "eyes a little downcast, standing in the office corridor, cool light, " + STYLE),

 # ── 第二幕 · 第三单（玩具）──
 "S17_pickup": dict(ref=True,
   prompt="medium shot at a parcel counter, " + HERO_SHORT +
          "**lifting a large cardboard toy box with both arms**, the box almost as wide as he is, "
          "a shop assistant behind the counter, warm indoor light, " + STYLE),

 "S18_deliver3": dict(ref=True,
   prompt="shot through an open door, " + HERO_SHORT +
          "seen from behind at the left edge handing over a big toy box, "
          "**a father takes it while a small child rushes out from behind and hugs his father's "
          "leg**, warm evening light from inside the flat, " + STYLE),

 "S19_corridor": dict(ref=True,
   prompt="medium wide shot, " + HERO_SHORT +
          "**standing alone in a dim stairwell landing, head slightly tilted toward a closed door, "
          "listening to the muffled laughter coming from inside**, hands empty at his sides, "
          "bare bulb, long shadows, very quiet, " + STYLE),

 # ── 第三幕 ──
 "S21_night": dict(ref=True,
   prompt="wide shot at night, " + HERO_SHORT +
          "riding his scooter down a dark city street, **his orange backpack and vest glowing "
          "warmly against the blue night**, street lamps and shop signs streaking past, "
          "wet asphalt reflections, moody, " + STYLE),

 "S23_stairs": dict(ref=True,
   prompt="medium wide shot, " + HERO_SHORT +
          "**climbing a dark old apartment stairwell carrying a paper food bag**, "
          "a bare flickering bulb above, green-painted walls, peeling paint, "
          "long shadow on the steps, dim and narrow, " + STYLE),

 "S24_knock": dict(ref=True,
   prompt="medium shot, " + HERO_SHORT +
          "**standing before a worn metal door with one hand raised to knock**, "
          "a paper food bag in the other hand, dim bare bulb overhead, "
          "green walls, narrow landing, " + STYLE),

 "S25_open": dict(ref=True,
   prompt="over-the-shoulder shot through a half-open door, " + HERO_SHORT +
          "seen from behind at the left edge, **a small girl with braided hair standing in the "
          "doorway looking up at him, head tilted**, warm orange birthday light and balloons "
          "behind her inside the flat, the corridor dark, gentle contrast, " + STYLE),

 "S26_gawp": dict(ref=True,
   prompt="close-up, " + HERO_DESC +
          "**frozen with his mouth slightly open for a beat, then breaking into a real warm "
          "smile, eyes curving shut**, warm light from the open door falling across his face, "
          "soft halftone shading, deeply tender, " + STYLE),

 "S27_cake": dict(ref=True,
   prompt="medium close shot, " + HERO_SHORT +
          "in a dim stairwell, **a woman's hand reaching out from the doorway pressing a slice "
          "of birthday cake into his hands**, warm light spilling from the flat, "
          "he looks down at the cake then up at her, surprised and moved, " + STYLE),

 "S28_steps": dict(ref=True,
   prompt="medium wide shot, " + HERO_SHORT +
          "**sitting alone on concrete steps outside an old apartment block at sunset**, "
          "a slice of cake on his knees, **striking a match and planting it upright in the cake "
          "like a candle**, the tiny flame bright, long warm shadows, empty street, deeply quiet, " + STYLE),

 "S29_blow": dict(ref=True,
   prompt="extreme close-up, " + HERO_DESC +
          "**chin and muzzle in profile, blowing out a single match stuck in a slice of cake**, "
          "a thin curl of smoke rising, warm rim light on his cheek, "
          "the tiny flame just dying, tender and quiet, " + STYLE),

 "S30_city": dict(ref=True,
   prompt="epic wide shot from a low rooftop, " + HERO_SHORT +
          "**seen small in the lower third from behind, head tilted up**, "
          "**a vast dense city of old low houses and new glass towers packed together, "
          "thousands of windows lit up at dusk**, a thin trail of smoke rising beside him, "
          "golden and deep blue sky, deeply emotional and hopeful, " + STYLE),
}

if __name__ == "__main__":
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    total = len(SHOTS)
    # ⛔ 实测：传 I2I 参考图（864×1152）单张要 575 秒（9.6 分钟），26 张要 4 小时。
    #    改用**纯文字描述**（角色锚点精确到色值和形状），换取速度。
    #    代价是角色会有漂移，所以描述里把每个识别点都写死。
    USE_REF = os.environ.get("USE_REF", "0") == "1"
    for i, (name, cfg) in enumerate(SHOTS.items(), 1):
        if only and not any(o in name for o in only):
            continue
        out = os.path.join(EP, name + ".png")
        if os.path.exists(out) and os.path.getsize(out) > 200000:
            print(f"  · [{i}/{total}] {name} 已存在", flush=True)
            continue
        print(f"  → [{i}/{total}] {name} {'[参考]' if USE_REF else ''} ...", flush=True)
        try:
            t0 = time.time()
            kw = dict(size="2K", ratio="16:9", save_to=out)
            if USE_REF:
                kw["init_images"] = [HERO]
            agnes.gen_image(cfg["prompt"], **kw)
            dt = time.time() - t0
            with open(os.path.splitext(out)[0] + ".prompt.txt", "w", encoding="utf-8") as f:
                json.dump({"prompt": cfg["prompt"], "ref": USE_REF,
                           "elapsed_s": round(dt, 1)}, f, ensure_ascii=False, indent=2)
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
        except Exception as e:
            print(f"    ✗ {str(e)[:150]}", flush=True)
    print(f"\n→ {EP}", flush=True)
