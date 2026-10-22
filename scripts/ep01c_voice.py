#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP01c《第一万单》· 配音

相对上一版的关键改动：
  新增 V08「还差三单。」——**把中间省略的订单数用一句台词交代掉**，
  观众才不会觉得"跳了"。这是"故事讲清楚"的一部分：
  宁可说一句，也不要让观众自己补。

声线沿用：阿甘=云希（少年）／店员=云希加速／保安=云健（大叔）／
         小女孩=云夏+30Hz／妈妈=晓伊／旁白=云夏
"""
import asyncio
import json
import os
import re

import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = os.path.join(ROOT, "work", "ep01c", "audio")
os.makedirs(AUD, exist_ok=True)

AGAN = "zh-CN-YunxiNeural"
GUARD = "zh-CN-YunjianNeural"
GIRL = "zh-CN-YunxiaNeural"
MOM = "zh-CN-XiaoyiNeural"
NARR = "zh-CN-YunxiaNeural"

LINES = [
 ("V01", "今天是个大日子。", AGAN, +8, "+3Hz", "小小得意"),
 ("V02", "没人记得，那就自己记住。", AGAN, +2, "+2Hz", "自嘲但坚定"),
 ("V03", "甘骡八——第一万单，出发！", AGAN, +22, "+6Hz", "兴奋"),
 ("V04", "快点快点，客人都在催了！", AGAN, +30, "+12Hz", "店员急躁"),
 ("V05", "马上马上。", AGAN, +25, "+8Hz", "手忙脚乱"),
 ("V06", "骑手走地库。", GUARD, -8, "-5Hz", "保安冷漠"),
 ("V07", "叔，就一分钟——", AGAN, +12, "+4Hz", "讨好"),
 ("V08", "还差三单。", AGAN, -14, "-3Hz", "★自己给自己打气"),
 ("V09", "您好——外卖。", AGAN, -5, "+0Hz", "平静"),
 ("V10", "叔叔，你也有蛋糕吗？", GIRL, +10, "+30Hz", "孩童天真"),
 ("V11", "有啊。我也有。", AGAN, -8, "+2Hz", "★强撑的笑"),
 ("V12", "拿着，一块吃啊。", MOM, +5, "+2Hz", "妈妈热情"),
 ("V13", "……许个愿吧。", AGAN, -20, "-3Hz", "★极轻，几乎自语"),
 ("V14", "那夜，我爸犯了错，然后有了我。但在骡马城，谁又不是个美丽的意外呢？",
        NARR, -12, "-3Hz", "旁白收尾"),
]


async def synth(lid, text, voice, rate, pitch, retries=4):
    path = os.path.join(AUD, lid + ".mp3")
    for a in range(retries):
        try:
            c = edge_tts.Communicate(text, voice, rate=f"{rate:+d}%", pitch=pitch)
            buf, bounds = bytearray(), []
            async for ch in c.stream():
                if ch["type"] == "audio":
                    buf += ch["data"]
                elif ch["type"] in ("SentenceBoundary", "WordBoundary"):
                    bounds.append({"start": ch["offset"] / 1e7,
                                   "end": (ch["offset"] + ch["duration"]) / 1e7,
                                   "text": ch.get("text", "").strip()})
            if len(buf) < 500:
                raise RuntimeError("过小")
            with open(path, "wb") as f:
                f.write(buf)
            return bounds
        except Exception as e:
            if a == retries - 1:
                print(f"    ✗ {lid}: {str(e)[:100]}")
                return None
            await asyncio.sleep(2 * (a + 1))
    return None


def clean(t):
    return re.sub(r"\s+([，。！？；：、—])", r"\1", t).strip()


async def main():
    meta = {}
    print(f"{'id':5s} {'声音':16s} {'时长':>6s}  {'情绪':16s} 台词")
    print("-" * 92)
    for lid, text, voice, rate, pitch, mood in LINES:
        b = await synth(lid, text, voice, rate, pitch)
        if not b:
            continue
        rows = [{"start": round(x["start"], 3), "end": round(x["end"], 3),
                 "text": clean(x["text"])} for x in b]
        dur = rows[-1]["end"] if rows else 0
        meta[lid] = {"text": text, "voice": voice, "rate": rate, "pitch": pitch,
                     "mood": mood, "duration": round(dur, 3), "sentences": rows}
        v = voice.replace("zh-CN-", "").replace("Neural", "")
        print(f"{lid:5s} {v:16s} {dur:6.2f}s  {mood:16s} {text[:28]}")

    with open(os.path.join(AUD, "_timeline.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"\n台词 {len(meta)} 条，共 {sum(v['duration'] for v in meta.values()):.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
