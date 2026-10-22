#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
第一集 · 旁白与对白配音（edge-tts）
====================================

为什么用 edge-tts：
  · 免费、无需 key
  · 中文神经网络语音，质量远高于系统 SAPI
  · 命令行可批处理，可指定语速/音高/风格

角色声线设计：
  · 旁白 —— 云希（男声，温和），语速略慢，像回忆
  · 阿甘 —— 云健（男声，年轻有活力），语速略快，乐观
  · 老山羊 / 大狼狗 —— 云扬（男声，低沉），做对比

⚠️ 实测：edge-tts 需要联网访问微软服务，偶发超时，加重试。
"""
import asyncio
import json
import os
import sys

import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01")
AUD = os.path.join(EP, "audio")
os.makedirs(AUD, exist_ok=True)

# 声音
VOICE_NARRATOR = "zh-CN-YunxiNeural"     # 男，温和
VOICE_AGAN = "zh-CN-YunjianNeural"       # 男，年轻
VOICE_OLD = "zh-CN-YunyangNeural"        # 男，低沉，旁白/长者

LINES = [
    # (id, 文本, 声音, 语速%, 音高)
    ("L00_narrator_open",
     "那夜，我爸犯了错，然后有了我。他是匹英俊的赛马，我妈是头勤恳的母驴。"
     "大家说我是个错误，但在骡马城，谁又不是个美丽的意外呢？",
     VOICE_NARRATOR, -8, "-2Hz"),

    ("L01_sign",
     "来了骡马，就是骡马人。",
     VOICE_NARRATOR, -5, "-2Hz"),

    ("L02_mirror",
     "小甘小甘，今天也要元气满满，送出第一万单！",
     VOICE_AGAN, +6, "+3Hz"),

    ("L03_scooter",
     "橙蜜蜜让一让，红狗狗靠边走——黄袋鼠阿甘，来咯！",
     VOICE_AGAN, +10, "+4Hz"),

    ("L04_goat",
     "这小骡子，天天玩特技！",
     VOICE_OLD, -6, "-4Hz"),

    ("L05_lobby",
     "叔，这是八十八楼波斯猫总裁的无糖热燕麦。冷了她脾气，可比您还凶哦。",
     VOICE_AGAN, +4, "+2Hz"),

    ("L06_elevator",
     "生活很难，但我的单子，绝不超时。",
     VOICE_AGAN, -10, "+0Hz"),

    ("L07_rooftop",
     "明天见，骡马城。",
     VOICE_AGAN, -6, "+1Hz"),
]


async def one(text, voice, rate, pitch, out, retries=4):
    for i in range(retries):
        try:
            c = edge_tts.Communicate(text, voice, rate=f"{rate:+d}%", pitch=pitch)
            await c.save(out)
            if os.path.getsize(out) > 1000:
                return True
        except Exception as e:
            if i == retries - 1:
                print(f"    ✗ {os.path.basename(out)}: {str(e)[:100]}")
                return False
            await asyncio.sleep(2 * (i + 1))
    return False


async def main():
    meta = {}
    for lid, text, voice, rate, pitch in LINES:
        out = os.path.join(AUD, f"{lid}.mp3")
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            print(f"  · {lid} 已存在")
        else:
            ok = await one(text, voice, rate, pitch, out)
            print(f"  {'✓' if ok else '✗'} {lid}")
        if os.path.exists(out):
            meta[lid] = {"text": text, "voice": voice, "rate": rate,
                         "pitch": pitch, "file": os.path.basename(out),
                         "bytes": os.path.getsize(out)}
    with open(os.path.join(AUD, "_lines.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"\n共 {len(meta)} 条 → {AUD}")


if __name__ == "__main__":
    asyncio.run(main())
