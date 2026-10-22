#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP01b · 配音（人物性格修正版）

⛔ 用户反馈：「配音感觉怪怪的，不符合人物性格特色」

诊断（查证 Edge TTS 官方声音定位）：
    上一版阿甘用的是 **云健 YunjianNeural = 低沉浑厚大叔，38–55 岁，硬汉/武将**
    但阿甘是个少年感的乐观小骡子。
    **给 18 岁的角色配 45 岁的声音，怎么听都违和。**

    正确选择：**云希 YunxiNeural = 清爽阳光少年，18–27 岁，少年男主**
    官方推荐语速 1.2–1.6x（说明它天生适合快节奏、有活力的场景）

✅ 本版三条改法：
 1. **阿甘 → 云希**
 2. **同一个人不同情绪，靠语速+音高区分**，比换声音自然：
      欢快 +22% / 讨好 +12% / 失落 −18% / 极轻 −20%
 3. **配角各司其职**：
      店员 = 云希 +30%（同一声音加速就变急躁）
      保安 = 云健 −8%（大叔音在这里才合适）
      小女孩 = 晓双 XiaoshuangNeural（清脆孩童少女 8–14 岁）
      妈妈 = 晓伊 XiaoyiNeural（温柔治愈 25–35 岁）
      旁白 = 云夏 YunxiaNeural（稳重扎实，念最后一句要稳不能飘）
"""
import asyncio
import json
import os
import re

import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01b")
AUD = os.path.join(EP, "audio")
os.makedirs(AUD, exist_ok=True)

AGAN = "zh-CN-YunxiNeural"       # 少年男主（Novel 类，18-27 岁）
GUARD = "zh-CN-YunjianNeural"    # 大叔（Sports/Novel，38-55 岁）
# ⚠️ 实测：zh-CN 只有 8 个声音，**没有孩童女声**（Xiaoshuang 不存在）。
#    Xiaoyi 和 Yunxia 是唯二标注为 **Cartoon** 的声音。
#    小女孩用 Yunxia（正太童声 7-15 岁）+ 大幅抬高音高。
GIRL = "zh-CN-YunxiaNeural"
MOM = "zh-CN-XiaoyiNeural"       # 温柔女声（Cartoon）
NARR = "zh-CN-YunxiaNeural"      # 稳重（Cartoon）

# id, 台词, 声音, 语速%, 音高, 情绪说明, 镜号
LINES = [
 ("V01", "今天是个大日子。", AGAN, +8, "+3Hz", "小小得意", "S01"),
 ("V02", "没人记得，那就自己记住。", AGAN, +2, "+2Hz", "自嘲但坚定", "S02"),
 ("V03", "甘骡八——第一万单，出发！", AGAN, +22, "+6Hz", "兴奋喊出来", "S04"),
 ("V04", "快点快点，客人都在催了！", AGAN, +30, "+12Hz", "店员急躁（同声音加速）", "S05"),
 ("V05", "马上马上。", AGAN, +25, "+8Hz", "手忙脚乱", "S05"),
 ("V06", "骑手走地库。", GUARD, -8, "-5Hz", "保安冷漠", "S06"),
 ("V07", "叔，就一分钟——八十八楼，冷了她会不高兴的。", AGAN, +12, "+4Hz", "讨好陪笑", "S06"),
 ("V08", "……第五单。", AGAN, -18, "-4Hz", "★失落，最轻", "S08"),
 ("V09", "您好——外卖。", AGAN, -5, "+0Hz", "平静", "S10"),
 ("V10", "叔叔，你也有蛋糕吗？", GIRL, +10, "+30Hz", "孩童天真", "S11"),
 ("V11", "有啊。我也有。", AGAN, -8, "+2Hz", "★强撑的笑", "S12"),
 ("V12", "拿着，一块吃啊。", MOM, +5, "+2Hz", "妈妈热情", "S13"),
 ("V13", "……许个愿吧。", AGAN, -20, "-3Hz", "★极轻，几乎自语", "S14"),
 ("V14", "那夜，我爸犯了错，然后有了我。但在骡马城，谁又不是个美丽的意外呢？",
        NARR, -12, "-3Hz", "旁白收尾", "S15"),
]


async def synth(lid, text, voice, rate, pitch, retries=4):
    path = os.path.join(AUD, lid + ".mp3")
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
            if len(buf) < 600:
                raise RuntimeError("音频过小")
            with open(path, "wb") as f:
                f.write(buf)
            return bounds
        except Exception as e:
            if attempt == retries - 1:
                print(f"    ✗ {lid}: {str(e)[:120]}")
                return None
            await asyncio.sleep(2 * (attempt + 1))
    return None


def clean(t):
    return re.sub(r"\s+([，。！？；：、])", r"\1", t).strip()


async def main():
    meta = {}
    print(f"{'id':5s} {'角色声':22s} {'时长':>6s}  {'情绪':22s} 台词")
    print("-" * 100)
    for lid, text, voice, rate, pitch, mood, shot in LINES:
        bounds = await synth(lid, text, voice, rate, pitch)
        if not bounds:
            continue
        rows = [{"start": round(b["start"], 3), "end": round(b["end"], 3),
                 "text": clean(b["text"])} for b in bounds]
        dur = rows[-1]["end"] if rows else 0
        meta[lid] = {"text": text, "voice": voice, "rate": rate, "pitch": pitch,
                     "mood": mood, "shot": shot, "duration": round(dur, 3),
                     "sentences": rows}
        vshort = voice.replace("zh-CN-", "").replace("Neural", "")
        print(f"{lid:5s} {vshort:22s} {dur:6.2f}s  {mood:22s} {text[:26]}")

    with open(os.path.join(AUD, "_timeline.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    total = sum(v["duration"] for v in meta.values())
    print(f"\n台词总量 {total:.1f}s / 14 条（成片约 105s，其余全是留白和环境声）")


if __name__ == "__main__":
    asyncio.run(main())
