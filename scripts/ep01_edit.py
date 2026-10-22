#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
第一集 · 剪辑合成
================

输入：work/ep01/clips/S*.mp4（AI 生成的段）+ work/ep01/audio/L*.mp3（配音）
输出：release/骡马阿甘_EP01.mp4

流程：
  1. 每段按分镜目标时长裁剪（保证总长 28.6s）
  2. 配音按镜头时间点铺进去（先量每条配音实际时长，自动排）
  3. 生成 ASS 字幕并烧录（中文必须用 ASS，drawtext 会崩）
  4. 混音：对白 + 轻环境底（不盖人声）

⚠️ 铁律（上个项目的血泪）：
  · 只 trim 画面不 trim 声音 → 音画不同步。入出点必须一致。
  · 字幕时间必须是"检测出来的"不是"估计出来的"。
  · 中文路径 + drawtext 会崩，一律 ASS 烧录。
  · 用 -vf 就不能 -c:v copy。
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01")
CLIPS = os.path.join(EP, "clips")
AUD = os.path.join(EP, "audio")
OUT = os.path.join(ROOT, "release")
FF = r"C:/Users/87465/.workbuddy/binaries/python/envs/aitv/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"

# 分镜表：镜号, 目标时长, 字幕
SHOTS = [
    ("S1_alley_dawn", 3.4, "来了骡马，就是骡马人。"),
    ("S2_mirror_cap", 3.4, "小甘小甘，今天也要元气满满，送出第一万单！"),
    ("S3_scooter",    5.0, "橙蜜蜜让一让，红狗狗靠边走——黄袋鼠阿甘，来咯！"),
    ("S4_bridge",     3.4, "「这小骡子，天天玩特技！」"),
    ("S5_lobby",      5.0, "「叔，这是 88 楼波斯猫总裁的无糖热燕麦。」"),
    ("S6_elevator",   3.4, "生活很难，但我的单子，绝不超时。"),
    ("S7_rooftop",    5.0, "明天见，骡马城。"),
]

# ★ 配音时间轴：按**秒**铺，不是按镜头铺。
#   原因：旁白 L00 有 13.78 秒，塞不进 3.4 秒的镜头。
#   （这是上一版最大的设计错误——把长旁白硬塞进短镜头）
VOICEOVER = [
    # (配音 id, 起始秒, 最长可用秒, 是否允许加速)
    ("L00_narrator_open", 0.30, 13.40, False),   # 旁白横跨 S1-S4
    ("L05_lobby",         15.30, 4.80, True),    # S5 大堂
    ("L06_elevator",      20.30, 3.20, True),    # S6 电梯
    ("L07_rooftop",       23.80, 4.60, True),    # S7 天台
]

# 旁白分句字幕（按时间切，不靠估计——用 L00 的实际时长均分后再人工微调）
NARRATION_SUBS = [
    (0.30, 3.00, "那夜，我爸犯了错，然后有了我。"),
    (3.00, 6.60, "他是匹英俊的赛马，"),
    (6.60, 10.20, "我妈是头勤恳的母驴。"),
    (10.20, 13.60, "大家说我是个错误……"),
]

W, H = 1280, 704
FPS = 24


def run(args, **kw):
    r = subprocess.run([FF, "-y", "-v", "error"] + args, capture_output=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "ignore")[:400])
    return r


def dur_of(p):
    """精确时长（用 ffmpeg 解码计数，不信容器元数据）"""
    r = subprocess.run([FF, "-v", "error", "-i", p, "-f", "null", "-"],
                       capture_output=True)
    txt = r.stderr.decode("utf-8", "ignore")
    for line in txt.splitlines():
        if "time=" in line:
            t = line.split("time=")[1].split()[0]
            h, m, s = t.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    # 兜底：从 Duration 读
    r2 = subprocess.run([FF, "-i", p], capture_output=True)
    for line in r2.stderr.decode("utf-8", "ignore").splitlines():
        if "Duration" in line:
            t = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = t.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0


def make_ass(entries, out_path):
    """entries: [(start, end, text)]"""
    def ts(t):
        h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
        return f"{h}:{m:02d}:{s:05.2f}"

    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 704

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Microsoft YaHei,40,&H00F7F1E3,&H00F7F1E3,&H001A1410,&H001A1410,1,0,0,0,100,100,0,0,1,3.5,1.5,2,70,70,52,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for s, e, txt in entries:
        lines.append(f"Dialogue: 0,{ts(s)},{ts(e)},Sub,,0,0,0,,{txt}")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(head + "\n".join(lines) + "\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    seg_files, subs = [], []
    t = 0.0

    # ── 1. 逐段裁剪到目标时长（画面和声音一起裁）──
    norm = os.path.join(EP, "_norm")
    os.makedirs(norm, exist_ok=True)
    for name, target, sub in SHOTS:
        src = os.path.join(CLIPS, name + ".mp4")
        if not os.path.exists(src):
            print(f"  ! 缺 {name}，跳过")
            continue
        dst = os.path.join(norm, name + ".mp4")
        # 用 -t 同时裁画面和音频，保证同步
        run(["-i", src, "-t", f"{target:.3f}",
             "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                    f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
             "-c:v", "libx264", "-preset", "medium", "-crf", "19",
             "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
             dst])
        seg_files.append(dst)
        t += target

    total = t
    print(f"  片段 {len(seg_files)} 段，总长 {total:.2f}s")

    # 字幕时间轴：旁白分句 + 后段对白
    st = 0.0
    shot_t = []
    for name, target, sub in SHOTS:
        shot_t.append((name, st, st + target, sub))
        st += target
    subs += list(NARRATION_SUBS)
    for name, a, b, sub in shot_t:
        if a >= 15.0:            # 旁白结束后的镜头才用对白字幕
            subs.append((a + 0.2, b - 0.2, sub))

    # ── 2. 拼接（先拼，再统一贴音轨，避免逐段音画错位）──
    lst = os.path.join(norm, "_list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for s in seg_files:
            f.write("file '%s'\n" % s.replace("\\", "/"))
    vcat = os.path.join(norm, "_vcat.mp4")
    run(["-f", "concat", "-safe", "0", "-i", lst,
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-an", vcat])
    # 重校时间戳（concat 会留 pts 跳跃）
    vfix = os.path.join(norm, "_vfix.mp4")
    run(["-i", vcat, "-vf", f"fps={FPS},setpts=N/{FPS}/TB,settb=1/{FPS},setsar=1",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-an", vfix])

    # ── 3. 配音铺轨 ──
    # ⛔ 关键坑：`-f lavfi -i anullsrc` 是第 0 个输入，
    #    所以所有真实输入的索引要从 **1** 开始。
    #    （上一版从 0 开始，导致第一条配音被应用到了静音源上，整片第一条旁白消失）
    inputs = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    filters = []
    mix_in = []
    idx = 1
    for lid, start, max_len, allow_tempo in VOICEOVER:
        mp3 = os.path.join(AUD, lid + ".mp3")
        if not os.path.exists(mp3) or os.path.getsize(mp3) < 500:
            print(f"  ! 缺配音 {lid}")
            continue
        d = dur_of(mp3)
        tempo = 1.0
        if allow_tempo and d > max_len:
            tempo = min(1.6, d / max_len)     # 上限 1.6，再快就听不清了
        ms = int(start * 1000)
        inputs += ["-i", mp3]                 # ← 必须加进输入列表
        af = f"[{idx}:a]"
        if tempo > 1.001:
            af += f"atempo={tempo:.3f},"
        af += f"adelay={ms}|{ms}[vo{idx}]"
        filters.append(af)
        mix_in.append(f"[vo{idx}]")
        eff = d / tempo
        print(f"    {lid:22s} {d:5.2f}s → 起 {start:5.2f}s  "
              f"{'x%.2f ' % tempo if tempo > 1.001 else '原速 '} 占 {eff:5.2f}s")
        idx += 1

    # 环境底（填住人声停顿，但不盖人声）
    # ⚠️ 实测：a=0.030/vol=0.45 时停顿会掉到 -51dB，听感像"声音断了"。
    #    提到 a=0.10/vol=0.85 后约 -33dB，正好是"安静但没死"的区间。
    bed = (f"anoisesrc=d={total}:c=brown:a=0.10,"
           f"lowpass=f=1200,volume=0.85,"
           f"afade=t=in:st=0:d=0.8,afade=t=out:st={max(0,total-1.5):.2f}:d=1.5[bed]")
    filters.append(bed)
    mix_all = "".join(mix_in) + "[bed]"
    filters.append(f"{mix_all}amix=inputs={len(mix_in)+1}:normalize=0:"
                   f"dropout_transition=0[mix]")
    filters.append("[mix]alimiter=limit=0.94[aout]")

    mixed = os.path.join(EP, "_mix.m4a")
    run(inputs +
        ["-filter_complex", ";".join(filters),
         "-map", "[aout]", "-t", f"{total:.3f}",
         "-c:a", "aac", "-b:a", "192k", mixed])

    # ── 4. 字幕（ASS 烧录）──
    ass = os.path.join(EP, "_sub.ass")
    make_ass(subs, ass)
    ass_esc = ass.replace("\\", "/").replace(":", "\\:")

    # ── 5. 合成 ──
    final = os.path.join(OUT, "骡马阿甘_EP01.mp4")
    run(["-i", vfix, "-i", mixed,
         "-vf", f"ass='{ass_esc}'",
         "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18",
         "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-shortest", final])

    print(f"\n✓ {final}")
    print(f"  {dur_of(final):.2f}s  {os.path.getsize(final)//1024} KB")
    with open(os.path.join(EP, "_timeline.json"), "w", encoding="utf-8") as f:
        json.dump({"total": total, "shots": SHOTS,
                   "subs": [{"start": a, "end": b, "text": c} for a, b, c in subs]},
                  f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
