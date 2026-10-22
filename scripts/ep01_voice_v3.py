#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP01 · 配音 v3（节奏重构版）

变化（相对 v2）：
  1. **旁白拆成 4 段**，不再是一整条 13.78s 硬塞前 4 镜
  2. **最重的一句搬进电梯**："大家说我是个错误" → S6（他一个人对着镜子）
  3. **"谁又不是个美丽的意外呢"搬到天台** → S7（画面正好是这座城）
     这样画面和情绪咬合，而不是只当信息念出来
  4. 补回 S3/S4 的对白（v2 因旁白占满而被废弃）

所有台词都带 **SentenceBoundary 精确时间戳**。
"""
import asyncio
import json
import os
import re

import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01")
AUD = os.path.join(EP, "audio_v3")
os.makedirs(AUD, exist_ok=True)

V_NARR = "zh-CN-YunxiNeural"
V_AGAN = "zh-CN-YunjianNeural"
V_OLD = "zh-CN-YunyangNeural"

# id, 逐字稿, 声音, 语速%, 音高
LINES = [
 ("N1_night",  "那夜，我爸犯了错，然后有了我。", V_NARR, -12, "-3Hz"),
 ("N2_father", "他是匹英俊的赛马，我妈是头勤恳的母驴。", V_NARR, -8, "-2Hz"),
 ("D3_ride",   "橙蜜蜜让一让，红狗狗靠边走——黄袋鼠阿甘，来咯！", V_AGAN, +10, "+4Hz"),
 ("D4_goat",   "这小骡子，天天玩特技！", V_OLD, -6, "-4Hz"),
 ("D5_lobby",  "叔，这是八十八楼波斯猫总裁的无糖热燕麦。", V_AGAN, +4, "+2Hz"),
 ("N6_mistake", "大家说我是个错误。", V_NARR, -14, "-3Hz"),
 ("N7_accident", "但在骡马城，谁又不是个美丽的意外呢？", V_NARR, -10, "-2Hz"),
 ("D7_tomorrow", "明天见，骡马城。", V_AGAN, -8, "+1Hz"),
]


async def synth(lid, text, voice, rate, pitch, retries=4):
    audio = os.path.join(AUD, lid + ".mp3")
    for attempt in range(retries):
        try:
            comm = edge_tts.Communicate(text, voice, rate=f"{rate:+d}%", pitch=pitch)
            buf, bounds = bytearray(), []
            async for ch in comm.stream():
                if ch["type"] == "audio":
                    buf += ch["data"]
                elif ch["type"] in ("SentenceBoundary", "WordBoundary"):
                    bounds.append({"start": ch["offset"] / 1e7,
                                   "end": (ch["offset"] + ch["duration"]) / 1e7,
                                   "text": ch.get("text", "").strip()})
            if len(buf) < 800:
                raise RuntimeError("音频过小")
            with open(audio, "wb") as f:
                f.write(buf)
            return bounds
        except Exception as e:
            if attempt == retries - 1:
                print(f"    ✗ {lid}: {str(e)[:120]}")
                return None
            await asyncio.sleep(2 * (attempt + 1))
    return None


def clean(t):
    return re.sub(r"\s+([，。！？；：])", r"\1", t).strip()


async def main():
    meta = {}
    for lid, text, voice, rate, pitch in LINES:
        print(f"  → {lid}")
        bounds = await synth(lid, text, voice, rate, pitch)
        if not bounds:
            continue
        rows = [{"start": round(b["start"], 3), "end": round(b["end"], 3),
                 "text": clean(b["text"])} for b in bounds]
        dur = rows[-1]["end"] if rows else 0
        meta[lid] = {"text": text, "voice": voice, "rate": rate, "pitch": pitch,
                     "duration": round(dur, 3), "sentences": rows}
        print(f"    ✓ {dur:.2f}s  {len(rows)} 句  「{rows[0]['text'] if rows else ''}」")

    with open(os.path.join(AUD, "_timeline.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("\n--- 时长预算核对 ---")
    BUDGET = {"N1_night": 4.4, "N2_father": 2.2, "D3_ride": 3.9, "D4_goat": 2.1,
              "D5_lobby": 2.9, "N6_mistake": 2.9, "N7_accident": 2.9,
              "D7_tomorrow": 2.6}
    for k, v in meta.items():
        b = BUDGET.get(k, 0)
        flag = "✓" if v["duration"] <= b else f"⚠ 超 {v['duration']-b:+.2f}s，需加速"
        print(f"  {k:14s} {v['duration']:5.2f}s / 预算 {b:4.1f}s  {flag}")


if __name__ == "__main__":
    asyncio.run(main())
