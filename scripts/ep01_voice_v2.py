#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
第一集 · 配音 + 精确字幕时间轴（v2）

⛔ 为什么重做（用户："字幕语言没有对上"）
   上一版错在两点：
   1. 字幕是**我手写的摘要**，不是配音的逐字稿——
      旁白最后一句"但在骡马城，谁又不是个美丽的意外呢？"配音说了但没字幕；
      大堂后半句"冷了她脾气，可比您还凶哦"也一样。
   2. 字幕时间是**我估的**，不是量出来的。

✅ 本版做法：
   edge-tts 的边界事件拿**真实语音时间戳**。
   ⚠️ 实测 edge-tts 7.3.1 返回的是 `SentenceBoundary`（句级），不是 WordBoundary，
      offset/duration 单位 100ns（除 1e7 得秒）。这正好就是句级字幕要的东西。

   这正是《走蛟》那条铁律：**字幕时间必须是"检测出来的"不是"估计出来的"。**
"""
import asyncio
import json
import os
import re
import sys

import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01")
AUD = os.path.join(EP, "audio_v2")
os.makedirs(AUD, exist_ok=True)

V_NARR = "zh-CN-YunxiNeural"
V_AGAN = "zh-CN-YunjianNeural"

# 每条：id, 逐字稿（配音会逐字念）, 声音, 语速, 音高
LINES = [
 ("L00_narrator_open",
  "那夜，我爸犯了错，然后有了我。他是匹英俊的赛马，我妈是头勤恳的母驴。"
  "大家说我是个错误，但在骡马城，谁又不是个美丽的意外呢？",
  V_NARR, -8, "-2Hz"),

 ("L05_lobby",
  "叔，这是八十八楼波斯猫总裁的无糖热燕麦。冷了她脾气，可比您还凶哦。",
  V_AGAN, +4, "+2Hz"),

 ("L06_elevator",
  "生活很难，但我的单子，绝不超时。",
  V_AGAN, -10, "+0Hz"),

 ("L07_rooftop",
  "明天见，骡马城。",
  V_AGAN, -6, "+1Hz"),
]


async def synth(lid, text, voice, rate, pitch, retries=4):
    audio = os.path.join(AUD, lid + ".mp3")
    for attempt in range(retries):
        try:
            comm = edge_tts.Communicate(text, voice, rate=f"{rate:+d}%", pitch=pitch)
            buf = bytearray()
            bounds = []
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    buf += chunk["data"]
                elif chunk["type"] in ("SentenceBoundary", "WordBoundary"):
                    bounds.append({
                        "kind": chunk["type"],
                        "start": chunk["offset"] / 1e7,
                        "end": (chunk["offset"] + chunk["duration"]) / 1e7,
                        "text": chunk.get("text", ""),
                    })
            if len(buf) < 1000:
                raise RuntimeError("音频过小")
            with open(audio, "wb") as f:
                f.write(buf)
            return bounds
        except Exception as e:
            if attempt == retries - 1:
                print(f"    ✗ {lid}: {str(e)[:140]}")
                return None
            await asyncio.sleep(2 * (attempt + 1))
    return None


def main_of_bound(b):
    """句边界文本可能带多余空格（如 '有了我 。'），清理一下"""
    t = b.get("text", "")
    t = re.sub(r"\s+([，。！？；：])", r"\1", t)
    return t.strip()


async def main():
    meta = {}
    for lid, text, voice, rate, pitch in LINES:
        print(f"  → {lid}")
        bounds = await synth(lid, text, voice, rate, pitch)
        if not bounds:
            continue
        sents = [b for b in bounds if b["kind"] == "SentenceBoundary"]
        if not sents:
            print(f"    ! 无句边界事件，只有 {len(bounds)} 个其它事件")
            continue
        rows = [{"start": round(b["start"], 3), "end": round(b["end"], 3),
                 "text": main_of_bound(b)} for b in sents]
        dur = rows[-1]["end"] if rows else 0
        meta[lid] = {"text": text, "voice": voice, "rate": rate,
                     "pitch": pitch, "duration": round(dur, 3), "sentences": rows}
        print(f"    ✓ {len(rows)} 句 / 语音 {dur:.2f}s")
        for r in rows:
            print(f"      {r['start']:6.2f}-{r['end']:6.2f}  {r['text']}")

    with open(os.path.join(AUD, "_subtitle_timeline.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    n = sum(len(v["sentences"]) for v in meta.values())
    print(f"\n共 {n} 句字幕 → {AUD}/_subtitle_timeline.json")


if __name__ == "__main__":
    asyncio.run(main())
