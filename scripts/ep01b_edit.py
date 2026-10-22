#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP01b《今天的生日》· 剪辑合成
============================

15 镜 / 约 105 秒 / 环境音按情绪分层 / 四处留白 / 首尾淡入淡出

节奏设计（吸 → 呼）：
  S01 慢 6  ← 起：安静，只有他和镜子
  S02 慢 7  ← 自嘲，情绪落点
  S03 中 5  ← 出门
  S04 快 7  ← 加速
  S05 快 6
  S06 快 7  ← 最快
  S07 慢 6  ← ★呼吸①（电梯，无台词）
  S08 慢 5  ← 失落
  S09 慢 7  ← ★呼吸②（看别人的生日，无台词）
  S10 中 6
  S11 慢 8  ← ★呼吸③（小女孩开门，画面停住）
  S12 慢 6  ← 他笑了
  S13 中 7
  S14 长 9  ← ★呼吸④（台阶，留白）
  S15 长 10 ← 收
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01b")
AUD = os.path.join(EP, "audio")
CLIPS = os.path.join(EP, "clips")
OUT = os.path.join(ROOT, "release")
FF = r"C:/Users/87465/.workbuddy/binaries/python/envs/aitv/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"

W, H, FPS = 1280, 704, 24

# 镜号: 目标时长, 环境音量, [(配音id, 段内起点)]
# ⚠️ 配音起点必须保证 起点+配音时长 ≤ 段时长，否则尾巴会被切掉：
#    V06 2.32s / V07 4.40s → S06 必须 ≥ 2.50+4.40 = 6.90，给 7.6
#    V14 8.76s → S15 必须 ≥ 1.30+8.76 = 10.06，给 11.0（结尾本来就该长）
TIMELINE = [
 ("S01_room",        6.0, 0.052, [("V01", 0.90)]),
 ("S02_mirror",      7.0, 0.045, [("V02", 1.30)]),
 ("S03_door",        5.0, 0.070, []),
 ("S04_ride",        7.0, 0.100, [("V03", 1.10)]),
 ("S05_shop",        6.0, 0.110, [("V04", 0.60), ("V05", 3.40)]),
 ("S06_lobby",       7.6, 0.075, [("V06", 0.60), ("V07", 2.50)]),
 ("S07_elevator",    6.0, 0.030, []),                       # ★呼吸①
 ("S08_door_close",  5.0, 0.035, [("V08", 1.20)]),
 ("S09_window",      7.0, 0.028, []),                       # ★呼吸②
 ("S10_knock",       6.0, 0.050, [("V09", 0.90)]),
 ("S11_girl",        8.0, 0.032, [("V10", 1.40)]),          # ★呼吸③
 ("S12_smile",       6.0, 0.038, [("V11", 1.60)]),
 ("S13_cake",        7.0, 0.055, [("V12", 1.10)]),
 ("S14_steps",       9.0, 0.030, [("V13", 4.80)]),          # ★呼吸④
 ("S15_city",       11.0, 0.055, [("V14", 1.30)]),
]


def run(args):
    r = subprocess.run([FF, "-y", "-v", "error"] + args, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "ignore")[:600])


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
Style: Sub,Microsoft YaHei,42,&H00F7F1E3,&H00F7F1E3,&H001A1410,&H001A1410,1,0,0,0,100,100,0.5,0,1,3.5,1.5,2,80,80,52,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [f"Dialogue: 0,{ts(a)},{ts(b)},Sub,,0,0,0,,{c}" for a, b, c in entries]
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(head + "\n".join(lines) + "\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    norm = os.path.join(EP, "_norm")
    os.makedirs(norm, exist_ok=True)

    with open(os.path.join(AUD, "_timeline.json"), encoding="utf-8") as f:
        TL = json.load(f)

    # ── 1. 每段整理到目标时长 ──
    segs, starts = [], []
    t = 0.0
    for name, target, lvl, vos in TIMELINE:
        src = os.path.join(CLIPS, name + ".mp4")
        if not os.path.exists(src):
            print(f"  ! 缺 {name}")
            continue
        dst = os.path.join(norm, name + ".mp4")
        sd = dur_of(src)
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
              f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS}")
        if sd < target - 0.05:
            # 素材不够：放慢（上限 1.35）+ 尾部冻结
            ratio = min(1.35, target / sd)
            covered = sd * ratio
            vf2 = vf + f",setpts=PTS*{ratio:.4f}"
            if covered < target - 0.05:
                vf2 += f",tpad=stop_mode=clone:stop_duration={target - covered + 0.3:.3f}"
            run(["-i", src, "-vf", vf2, "-t", f"{target:.3f}",
                 "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                 "-pix_fmt", "yuv420p", dst])
            print(f"  {name:16s} {sd:5.2f}s→{target:.1f}s 放慢x{ratio:.2f}")
        else:
            run(["-i", src, "-t", f"{target:.3f}", "-vf", vf,
                 "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                 "-pix_fmt", "yuv420p", dst])
            print(f"  {name:16s} {sd:5.2f}s→{target:.1f}s 裁")
        segs.append(dst)
        starts.append(t)
        t += target
    print(f"  设计总长 {t:.2f}s")

    # ── 2. 拼接 ──
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

    # ⛔ 必须用实测时长（上一版用设计值导致淡出完全没出现）
    real_total = dur_of(vfix)
    print(f"  实际拼接 {real_total:.2f}s（设计 {t:.2f}s）")
    total = real_total

    # ── 3. 配音 + 字幕 ──
    inputs = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    filters, mix_in, subs = [], [], []
    idx = 1
    for (name, target, lvl, vos), st in zip(TIMELINE, starts):
        for lid, at in vos:
            mp3 = os.path.join(AUD, lid + ".mp3")
            if not os.path.exists(mp3):
                print(f"  ! 缺配音 {lid}")
                continue
            inputs += ["-i", mp3]
            ms = int((st + at) * 1000)
            filters.append(f"[{idx}:a]adelay={ms}|{ms}[vo{idx}]")
            mix_in.append(f"[vo{idx}]")
            idx += 1
            for row in TL.get(lid, {}).get("sentences", []):
                subs.append((round(st + at + row["start"], 2),
                             round(st + at + row["end"], 2),
                             row["text"]))

    # 环境音：按段落音量（时间点从 starts 推，绝不错位）
    bed_pts = []
    for (name, target, lvl, vos), st in zip(TIMELINE, starts):
        bed_pts.append((st, lvl))
        bed_pts.append((st + target, lvl))
    bed_pts.append((total, 0.004))
    parts = []
    for i in range(len(bed_pts) - 1):
        (t0, a0), (t1, a1) = bed_pts[i], bed_pts[i + 1]
        span = max(0.01, t1 - t0)
        parts.append(f"if(between(t,{t0:.3f},{t1:.3f}),"
                     f"{a0:.4f}+({a1-a0:+.4f})*(t-{t0:.3f})/{span:.3f},")
    expr = "".join(parts) + "0.05" + ")" * len(parts)

    filters.append(
        f"anoisesrc=d={total}:c=brown:a=1,lowpass=f=1300,"
        f"volume='{expr}':eval=frame,"
        f"afade=t=in:st=0:d=1.5,afade=t=out:st={max(0,total-2.5):.2f}:d=2.5[bed]")
    mix_in.append("[bed]")
    filters.append(f"{''.join(mix_in)}amix=inputs={len(mix_in)}:normalize=0:"
                   f"dropout_transition=0[mix]")
    filters.append("[mix]alimiter=limit=0.94[aout]")

    mixed = os.path.join(EP, "_mix.m4a")
    run(inputs + ["-filter_complex", ";".join(filters),
                  "-map", "[aout]", "-t", f"{total:.3f}",
                  "-c:a", "aac", "-b:a", "192k", mixed])

    # ── 4. 字幕 + 淡入淡出 + 合成 ──
    subs.sort()
    ass = os.path.join(EP, "_sub.ass")
    make_ass(subs, ass)
    print(f"\n  字幕 {len(subs)} 条")
    for a, b, c in subs:
        print(f"    {a:6.2f}-{b:6.2f}  {c}")

    ass_esc = ass.replace("\\", "/").replace(":", "\\:")
    vf_final = (f"ass='{ass_esc}',"
                f"fade=t=in:st=0:d=0.6,"
                f"fade=t=out:st={max(0,total-1.8):.2f}:d=1.8")
    final = os.path.join(OUT, "骡马阿甘_EP01_今天的生日.mp4")
    run(["-i", vfix, "-i", mixed,
         "-vf", vf_final,
         "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18",
         "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-shortest", final])

    print(f"\n✓ {final}")
    print(f"  {dur_of(final):.2f}s  {os.path.getsize(final)//1024} KB")


if __name__ == "__main__":
    main()
