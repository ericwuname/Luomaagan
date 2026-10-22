#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP01c《第一万单》· 剪辑（复用 ep01b 素材 + 补拍关键镜）

⛔ 背景：API 生图慢到 5-10 分钟/张，26 镜全做要 4 小时。
   ep01b 已有 15 段高质量素材，**覆盖了新剧本的大部分镜头**。

✅ 本版结构（18 镜）：
   · 4 个手机屏幕镜头（程序渲染，精确交代 9996 → 9997 → 10000）
   · 12 个复用 ep01b 的镜头
   · 2 个补拍的关键镜（"送蛋糕给一家人" / "送玩具给父子"）
     → 这两个和"开门小女孩"形成**三次门开的重复结构**，
       观众自己就能明白"他一直在送别人的生日"

故事清晰度的四条支柱：
  ① S01 手机"9996 单" → 身份 + 里程碑（一句话不用旁白）
  ② 三次门开（蛋糕 / 玩具 / 小女孩）→ 重复 → 预期
  ③ "还差三单" → 把中间省略的单数交代掉，不糊弄
  ④ 三次别人的笑 + 他三次的脸 → 对比不用说服
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, "work", "ep01b", "clips")   # 复用素材
C = os.path.join(ROOT, "work", "ep01c", "clips")   # 新素材
AUD = os.path.join(ROOT, "work", "ep01c", "audio")
OUT = os.path.join(ROOT, "release")
FF = r"C:/Users/87465/.workbuddy/binaries/python/envs/aitv/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"

W, H, FPS = 1280, 704, 24

# 镜号, 素材路径, 目标时长, 环境音量, [(配音id, 段内起点)], 备注
#
# ★ 结构改动（原计划"三次门开"生不出来，换成更好的）：
#   他**一直在门外** —— 门关上（09）→ 隔着窗看（10）→ 门终于为他开了（13）。
#   这个递进比"三次门开"更含蓄，也更准：他不是被欢迎的人，他是送东西的人。
TIMELINE = [
 ("01_phone9996",  os.path.join(C, "S01_phone.mp4"),  6.0, 0.040, [], "身份：今日已送达 9996 单"),
 ("02_bed",        os.path.join(B, "S01_room.mp4"),   6.0, 0.050, [("V01", 0.90)], "出租屋贴纸旗"),
 ("03_mirror",     os.path.join(B, "S02_mirror.mp4"), 6.5, 0.045, [("V02", 1.20)], "镜子自嘲"),
 ("04_phone9997",  os.path.join(C, "S04_phone.mp4"),  5.0, 0.055, [], "9997 单，仪式起"),
 ("05_ride",       os.path.join(B, "S04_ride.mp4"),   6.5, 0.100, [("V03", 1.00)], "骑车出发"),
 ("06_cakeshop",   os.path.join(C, "S06_cakeshop.mp4"), 6.5, 0.080, [("V15", 0.80)], "★蛋糕店取单（第一次出现生日）"),
 ("07_shop",       os.path.join(B, "S05_shop.mp4"),   6.0, 0.110, [("V04", 0.60), ("V05", 3.30)], "奶茶店取单"),
 ("08_lobby",      os.path.join(B, "S06_lobby.mp4"),  7.0, 0.075, [("V06", 0.60), ("V07", 2.60)], "写字楼被拦"),
 ("09_closed",     os.path.join(B, "S08_door_close.mp4"), 5.5, 0.035, [("V08", 1.10)], "★门关上 · 还差三单"),
 ("10_window",     os.path.join(B, "S09_window.mp4"), 7.0, 0.028, [], "★隔窗看别人过生日"),
 ("11_phone10000", os.path.join(C, "S22_phone.mp4"),  5.5, 0.060, [], "第 10000 单"),
 ("12_knock",      os.path.join(B, "S10_knock.mp4"),  6.0, 0.050, [("V09", 0.90)], "敲门"),
 ("13_open",       os.path.join(B, "S11_girl.mp4"),   8.0, 0.030, [("V10", 1.40)], "★门为他开了 · 小女孩"),
 ("14_smile",      os.path.join(B, "S12_smile.mp4"),  6.0, 0.038, [("V11", 1.60)], "愣住，然后笑"),
 ("15_cake",       os.path.join(B, "S13_cake.mp4"),   7.0, 0.055, [("V12", 1.10)], "妈妈塞蛋糕"),
 ("16_steps",      os.path.join(B, "S14_steps.mp4"),  9.0, 0.028, [("V13", 4.60)], "★台阶插火柴"),
 ("17_city",       os.path.join(B, "S15_city.mp4"),  11.0, 0.055, [("V14", 1.30)], "★城市全景"),
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
    norm = os.path.join(ROOT, "work", "ep01c", "_norm")
    os.makedirs(norm, exist_ok=True)

    tl_path = os.path.join(AUD, "_timeline.json")
    TL = {}
    if os.path.exists(tl_path):
        with open(tl_path, encoding="utf-8") as f:
            TL = json.load(f)

    segs, starts, t = [], [], 0.0
    for name, src, target, lvl, vos, note in TIMELINE:
        if not os.path.exists(src):
            print(f"  ! 缺 {name}  ({os.path.basename(src)})")
            continue
        dst = os.path.join(norm, name + ".mp4")
        sd = dur_of(src)
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
              f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS}")
        if sd < target - 0.05:
            ratio = min(1.35, target / sd)
            covered = sd * ratio
            vf2 = vf + f",setpts=PTS*{ratio:.4f}"
            if covered < target - 0.05:
                vf2 += f",tpad=stop_mode=clone:stop_duration={target-covered+0.3:.3f}"
            run(["-i", src, "-vf", vf2, "-t", f"{target:.3f}", "-an",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                 "-pix_fmt", "yuv420p", dst])
            print(f"  {name:16s} {sd:5.2f}→{target:4.1f}s 放慢x{ratio:.2f}  {note}")
        else:
            run(["-i", src, "-t", f"{target:.3f}", "-vf", vf, "-an",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                 "-pix_fmt", "yuv420p", dst])
            print(f"  {name:16s} {sd:5.2f}→{target:4.1f}s 裁       {note}")
        segs.append(dst)
        starts.append(t)
        t += target
    print(f"  设计总长 {t:.2f}s")

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

    real_total = dur_of(vfix)
    print(f"  实际拼接 {real_total:.2f}s（设计 {t:.2f}s）")
    total = real_total

    # 配音 + 字幕
    inputs = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    filters, mix_in, subs = [], [], []
    idx = 1
    for (name, src, target, lvl, vos, note), st in zip(TIMELINE, starts):
        for lid, at in vos:
            mp3 = os.path.join(AUD, lid + ".mp3")
            if not os.path.exists(mp3):
                continue
            inputs += ["-i", mp3]
            ms = int((st + at) * 1000)
            filters.append(f"[{idx}:a]adelay={ms}|{ms}[vo{idx}]")
            mix_in.append(f"[vo{idx}]")
            idx += 1
            for row in TL.get(lid, {}).get("sentences", []):
                subs.append((round(st + at + row["start"], 2),
                             round(st + at + row["end"], 2), row["text"]))

    # 环境音按段落
    bed_pts = []
    for (name, src, target, lvl, vos, note), st in zip(TIMELINE, starts):
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

    mixed = os.path.join(ROOT, "work", "ep01c", "_mix.m4a")
    run(inputs + ["-filter_complex", ";".join(filters),
                  "-map", "[aout]", "-t", f"{total:.3f}",
                  "-c:a", "aac", "-b:a", "192k", mixed])

    subs.sort()
    ass = os.path.join(ROOT, "work", "ep01c", "_sub.ass")
    make_ass(subs, ass)
    print(f"\n  字幕 {len(subs)} 条")
    for a, b, c in subs:
        print(f"    {a:6.2f}-{b:6.2f}  {c}")

    ass_esc = ass.replace("\\", "/").replace(":", "\\:")
    vf_final = (f"ass='{ass_esc}',fade=t=in:st=0:d=0.6,"
                f"fade=t=out:st={max(0,total-1.8):.2f}:d=1.8")
    final = os.path.join(OUT, "骡马阿甘_EP01_第一万单.mp4")
    run(["-i", vfix, "-i", mixed, "-vf", vf_final,
         "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-shortest", final])

    print(f"\n✓ {final}")
    print(f"  {dur_of(final):.2f}s  {os.path.getsize(final)//1024} KB")


if __name__ == "__main__":
    main()
