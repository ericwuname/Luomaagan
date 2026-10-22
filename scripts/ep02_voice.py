#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP02 配音 + 门铃音效

⛔ 这一集最难的不是画面，是**鹦鹉的声音**。
   它必须听起来"像在学舌"，而不是一个普通人在念台词。
   如果鹦鹉听起来和人一样，整个笑点就塌了——因为它本来是"替代门铃"的。

✅ 三层做法
   1. **音源**：edge-tts 云夏（正太童声）+ 极高音高 + 明显加速 → 得到"尖、快"的底子
   2. **音色**：带通滤波 320–3600Hz（模拟鸟的发声窄带）+ 轻微颗粒失真
   3. **门铃动机**：程序合成两个电子音（叮=1318Hz / 咚=1046Hz），
      在鹦鹉说"叮咚"的位置**叠加真实门铃音**，
      让观众听到的确实是"门铃在响"，而不是"有人在说叮咚"

审查修改已并入：
   · D01b「记得五星好评」—— 给 16 镜鹦鹉学这句话找到出处
"""
import asyncio
import json
import os
import re
import subprocess

import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep02")
AUD = os.path.join(EP, "audio")
os.makedirs(AUD, exist_ok=True)
FF = (r"C:/Users/87465/.workbuddy/binaries/python/envs/aitv/Lib/"
      r"site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe")

AGAN = "zh-CN-YunxiNeural"      # 少年
PARROT = "zh-CN-YunxiaNeural"   # 正太童声，抬音高后像鸟
RABBIT = "zh-CN-XiaoyiNeural"   # 温柔女声，疲惫

# id, 台词, 声音, 语速, 音高, 情绪
LINES = [
 ("D01",  "今天我就是个影子。", AGAN, +4, "+2Hz", "一本正经，轻声，有点得意"),
 ("D01b", "记得五星好评。", AGAN, -10, "+0Hz", "★职业习惯的自语，很轻"),
 ("D02",  "叮咚——外卖到了！", PARROT, +26, "+62Hz", "★第一次，像真的门铃通知"),
 ("D03",  "我还没按呢……", AGAN, -8, "-2Hz", "气声、错愕"),
 ("D04",  "嘘！我在开会！", RABBIT, +6, "+4Hz", "压低声音，不是怒吼"),
 ("D05",  "嘘！我在开会！开会！", PARROT, +30, "+64Hz", "★比兔子明显大声"),
 ("D06",  "别说话……别说话……", AGAN, -18, "-3Hz", "极轻，怕惊动整栋楼"),
 ("D07",  "别说话！别说话！", PARROT, +34, "+66Hz", "★声量突然放大，形成反差"),
 ("D08",  "你按门铃了？", RABBIT, -6, "+2Hz", "压着火气"),
 ("D09",  "我真没按。", AGAN, -4, "+0Hz", "诚恳、简短"),
 ("D10",  "叮咚！外卖到了！麻烦点个五星好评！", PARROT, +28, "+62Hz", "★门铃节拍 + 骑手口吻"),
 ("D11",  "五星给你。门铃不是你按的。", RABBIT, -4, "+2Hz", "松一口气，带歉意"),
 ("D12",  "……一份，整层楼？", AGAN, -12, "-2Hz", "结尾低声吐槽"),
]

# ★ 鹦鹉的"鸟嗓"处理链
PARROT_CHAIN = ("highpass=f=320,lowpass=f=3600,"
                "acompressor=threshold=0.08:ratio=6:attack=3:release=90,"
                "aecho=0.8:0.9:12:0.18")


async def synth(lid, text, voice, rate, pitch, retries=4):
    raw = os.path.join(AUD, lid + "_raw.mp3")
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
            with open(raw, "wb") as f:
                f.write(buf)
            return raw, bounds
        except Exception as e:
            if a == retries - 1:
                print(f"    ✗ {lid}: {str(e)[:100]}")
                return None, None
            await asyncio.sleep(2 * (a + 1))
    return None, None


def make_bell(path, d1=1318.0, d2=1046.0, sr=24000):
    """合成电子门铃「叮—咚」：两个正弦 + 指数衰减 + 轻微二次谐波"""
    import numpy as np
    n1, n2 = int(0.42 * sr), int(0.55 * sr)
    t1 = np.arange(n1) / sr
    t2 = np.arange(n2) / sr
    a = (np.sin(2 * np.pi * d1 * t1) * 0.6 +
         np.sin(2 * np.pi * d1 * 2 * t1) * 0.18) * np.exp(-t1 * 9)
    b = (np.sin(2 * np.pi * d2 * t2) * 0.6 +
         np.sin(2 * np.pi * d2 * 2 * t2) * 0.18) * np.exp(-t2 * 7)
    sig = np.concatenate([a, b, np.zeros(int(0.06 * sr))])
    sig = np.clip(sig, -1, 1) * 0.55
    pcm = (sig * 32767).astype("<i2").tobytes()
    subprocess.run([FF, "-y", "-v", "error", "-f", "s16le", "-ar", str(sr),
                    "-ac", "1", "-i", "-", "-c:a", "libmp3lame", "-b:a", "192k", path],
                   input=pcm, check=True)
    return path


def postprocess(raw, out, is_parrot):
    """鹦鹉加鸟嗓链；其他人只做轻微压缩，保持自然"""
    if is_parrot:
        af = PARROT_CHAIN
    else:
        af = "acompressor=threshold=0.12:ratio=3:attack=8:release=180"
    subprocess.run([FF, "-y", "-v", "error", "-i", raw,
                    "-af", af, "-ar", "48000", "-ac", "2",
                    "-c:a", "aac", "-b:a", "192k", out], check=True)
    return out


def clean(t):
    return re.sub(r"\s+([，。！？；：、—])", r"\1", t).strip()


async def main():
    bell = make_bell(os.path.join(AUD, "bell.mp3"))
    print(f"门铃音效 → {bell}  {os.path.getsize(bell)//1024} KB\n")

    meta = {}
    print(f"{'id':5s} {'声音':14s} {'时长':>6s}  {'处理':8s} 台词")
    print("-" * 96)
    for lid, text, voice, rate, pitch, mood in LINES:
        raw, bounds = await synth(lid, text, voice, rate, pitch)
        if not raw:
            continue
        is_parrot = (voice == PARROT)
        out = os.path.join(AUD, lid + ".m4a")
        postprocess(raw, out, is_parrot)

        # 时长
        r = subprocess.run([FF, "-i", out], capture_output=True)
        dur = 0.0
        for line in r.stderr.decode("utf-8", "ignore").splitlines():
            if "Duration" in line:
                t = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = t.split(":")
                dur = int(h) * 3600 + int(m) * 60 + float(s)
                break

        rows = [{"start": round(b["start"], 3), "end": round(b["end"], 3),
                 "text": clean(b["text"])} for b in bounds]
        meta[lid] = {"text": text, "voice": voice, "rate": rate, "pitch": pitch,
                     "mood": mood, "duration": round(dur, 3),
                     "parrot_chain": is_parrot, "sentences": rows}
        v = voice.replace("zh-CN-", "").replace("Neural", "")
        print(f"{lid:5s} {v:14s} {dur:6.2f}s  {'鸟嗓' if is_parrot else '自然':8s} {text[:34]}")

    with open(os.path.join(AUD, "_timeline.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"\n共 {len(meta)} 条，台词总量 {sum(v['duration'] for v in meta.values()):.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
