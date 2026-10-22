#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
第一集 · 剪辑合成 v2

修了用户指出的两个问题：
  ① **运动方向不对** —— 在 ep01_video_v2.py 里重写了运镜 prompt（第一句写运镜+禁止方向）
  ② **字幕语言没对上** —— 字幕改为读 `audio_v2/_subtitle_timeline.json` 的
     **真实语音边界时间**，并且是**逐字稿**不是摘要（旁白 3 句、大堂 2 句全在）

关键：配音若被 atempo 加速，字幕时间必须同步除以 tempo，否则又对不上。
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01")
CLIPS = os.path.join(EP, "clips_v2")
AUD = os.path.join(EP, "audio_v2")
OUT = os.path.join(ROOT, "release")
FF = r"C:/Users/87465/.workbuddy/binaries/python/envs/aitv/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"

W, H, FPS = 1280, 704, 24

# 镜号 + 目标时长
SHOTS = [
    ("S1_alley_dawn", 3.4),
    ("S2_mirror_cap", 3.4),
    ("S3_scooter",    5.0),
    ("S4_bridge",     3.4),
    ("S5_lobby",      5.0),
    ("S6_elevator",   3.4),
    ("S7_rooftop",    5.0),
]

# 配音铺设：id, 起始秒, 允许的最大占用秒（超了才加速）, 是否允许加速
VO = [
    ("L00_narrator_open", 0.15, 14.5, False),
    ("L05_lobby",        15.30,  4.70, True),
    ("L06_elevator",     20.20,  3.10, True),
    ("L07_rooftop",      23.70,  4.60, False),
]


def run(args, **kw):
    r = subprocess.run([FF, "-y", "-v", "error"] + args, capture_output=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "ignore")[:500])


def dur_of(p):
    r = subprocess.run([FF, "-i", p], capture_output=True)
    for line in r.stderr.decode("utf-8", "ignore").splitlines():
        if "Duration" in line:
            t = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = t.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0


def ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def make_ass(entries, out_path):
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 704
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Microsoft YaHei,42,&H00F7F1E3,&H00F7F1E3,&H001A1410,&H001A1410,1,0,0,0,100,100,0.5,0,1,3.5,1.5,2,80,80,54,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [f"Dialogue: 0,{ts(a)},{ts(b)},Sub,,0,0,0,,{c}" for a, b, c in entries]
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(head + "\n".join(lines) + "\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    norm = os.path.join(EP, "_norm_v2")
    os.makedirs(norm, exist_ok=True)

    # ── 1. 逐段裁剪（画面音频一起裁）──
    segs, t = [], 0.0
    for name, target in SHOTS:
        src = os.path.join(CLIPS, name + ".mp4")
        if not os.path.exists(src):
            print(f"  ! 缺 {name}")
            continue
        dst = os.path.join(norm, name + ".mp4")
        run(["-i", src, "-t", f"{target:.3f}",
             "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                    f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
             "-c:v", "libx264", "-preset", "medium", "-crf", "19",
             "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", dst])
        segs.append(dst)
        t += target
    total = t
    print(f"  片段 {len(segs)} 段 / {total:.2f}s")

    # ── 2. 拼接 + 时间戳重校 ──
    lst = os.path.join(norm, "_list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for s in segs:
            f.write("file '%s'\n" % s.replace("\\", "/"))
    vcat = os.path.join(norm, "_vcat.mp4")
    run(["-f", "concat", "-safe", "0", "-i", lst,
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-an", vcat])
    vfix = os.path.join(norm, "_vfix.mp4")
    run(["-i", vcat, "-vf", f"fps={FPS},setpts=N/{FPS}/TB,settb=1/{FPS},setsar=1",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-an", vfix])

    # ── 3. 配音 + 字幕（时间随 tempo 同步缩放）──
    tl_path = os.path.join(AUD, "_subtitle_timeline.json")
    with open(tl_path, encoding="utf-8") as f:
        TL = json.load(f)

    inputs = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]  # 索引 0 是静音源！
    filters, mix_in = [], []
    subs = []
    idx = 1
    for lid, start, max_len, allow in VO:
        mp3 = os.path.join(AUD, lid + ".mp3")
        if not os.path.exists(mp3):
            print(f"  ! 缺配音 {lid}")
            continue
        d = dur_of(mp3)
        tempo = 1.0
        if allow and d > max_len:
            tempo = min(1.6, d / max_len)
        inputs += ["-i", mp3]
        ms = int(start * 1000)
        af = f"[{idx}:a]"
        if tempo > 1.001:
            af += f"atempo={tempo:.3f},"
        af += f"adelay={ms}|{ms}[vo{idx}]"
        filters.append(af)
        mix_in.append(f"[vo{idx}]")
        idx += 1

        # 字幕：真实时间 / tempo + start
        for row in TL.get(lid, {}).get("sentences", []):
            a = start + row["start"] / tempo
            b = start + row["end"] / tempo
            subs.append((round(a, 2), round(b, 2), row["text"]))
        print(f"    {lid:22s} {d:5.2f}s → {start:5.2f}s "
              f"{'x%.2f' % tempo if tempo > 1.001 else '原速'}  "
              f"{len(TL.get(lid, {}).get('sentences', []))} 句字幕")

    # 环境底（填停顿）
    filters.append(
        f"anoisesrc=d={total}:c=brown:a=0.10,lowpass=f=1200,volume=0.85,"
        f"afade=t=in:st=0:d=0.8,afade=t=out:st={max(0,total-1.5):.2f}:d=1.5[bed]")
    mix_in.append("[bed]")
    filters.append(f"{''.join(mix_in)}amix=inputs={len(mix_in)}:normalize=0:"
                   f"dropout_transition=0[mix]")
    filters.append("[mix]alimiter=limit=0.94[aout]")

    mixed = os.path.join(EP, "_mix_v2.m4a")
    run(inputs + ["-filter_complex", ";".join(filters),
                  "-map", "[aout]", "-t", f"{total:.3f}",
                  "-c:a", "aac", "-b:a", "192k", mixed])

    # ── 4. 字幕烧录 + 合成 ──
    subs.sort()
    ass = os.path.join(EP, "_sub_v2.ass")
    make_ass(subs, ass)
    print(f"  字幕 {len(subs)} 条")
    for a, b, c in subs:
        print(f"    {a:6.2f}-{b:6.2f}  {c}")

    ass_esc = ass.replace("\\", "/").replace(":", "\\:")
    final = os.path.join(OUT, "骡马阿甘_EP01_v2.mp4")
    run(["-i", vfix, "-i", mixed,
         "-vf", f"ass='{ass_esc}'",
         "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18",
         "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-shortest", final])

    print(f"\n✓ {final}")
    print(f"  {dur_of(final):.2f}s  {os.path.getsize(final)//1024} KB")


if __name__ == "__main__":
    main()
