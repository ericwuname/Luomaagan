#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP01 · 剪辑 v3 —— 节奏重构版（呼吸感）

⛔ 上一版为什么像赶场（用户原话）
   1. 镜头时长均匀：3.4/3.4/5/3.4/5/3.4/5 —— 没有起伏
   2. 违反「远长近短」：S6 是特写却给 3.4s
   3. 每个镜头都在"完成任务"，做完就切，没有"多余的时间"
   4. 没有空镜、没有反应镜头 —— 零留白
   5. **把 5 秒的台词硬压进 2.4 秒的镜头** ← 这条最致命，"赶"就是这里来的
   6. 结尾戛然而止

✅ 本版核心改动：**镜头时长服从台词的天然长度，而不是反过来**
   台词有多长，镜头就给多长（前后加气口），绝不加速到听不清。
   代价是总长从 28.6s 变成约 41s —— 但立项书本来就写「1-3 分钟/集」。

✅ 三处留白（这是"呼吸"的实体）
   ① S4b 刹车特写 0.9s（动作急停，无台词）
   ② S6 之后静帧 0.8s（他吸气前的一刻）
   ③ S8 城市空镜 3.0s（结尾呼气 + 淡出）

✅ 旁白重新分配（画面与情绪咬合）
   "大家说我是个错误" → 电梯里他对着镜子整理领带时
   "谁又不是个美丽的意外呢" → 天台看城市全景时
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01")
AUD = os.path.join(EP, "audio_v3")
CLIPS_AI = os.path.join(EP, "clips_v2")      # AI 生成的动作镜
CLIPS_KB = os.path.join(EP, "clips_kb")      # Ken Burns 精确镜
OUT = os.path.join(ROOT, "release")
FF = r"C:/Users/87465/.workbuddy/binaries/python/envs/aitv/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"

W, H, FPS = 1280, 704, 24

# ═══════════════════════════════════════════════════════════
#  时间轴（按台词天然长度排，含气口）
#  字段: 段名, 素材路径, 目标时长, 素材处理(slow/freeze/cut), 配音id, 配音起始, 说明
# ═══════════════════════════════════════════════════════════
def C(name):
    return os.path.join(CLIPS_AI, name + ".mp4")

SEGMENTS = [
    # ① 慢起：远景扫环境，旁白第一句
    dict(tag="S1", src=C("S1_alley_dawn"), dur=5.0, mode="slow",
         vo="N1_night", vo_at=0.45, fade_in=0.5,
         note="远景给足时间扫环境（远长）"),

    # ② 中景，旁白第二句（这句本身 4.83s，镜头跟着长）
    dict(tag="S2", src=C("S2_mirror_cap"), dur=5.3, mode="slow",
         vo="N2_father", vo_at=0.30,
         note="台词 4.83s，镜头服从台词"),

    # ③ 动作镜，阿甘对白（快）
    dict(tag="S3", src=C("S3_scooter"), dur=5.7, mode="slow",
         vo="D3_ride", vo_at=0.22,
         note="骑车欢快段，语速本就快"),

    # ④ 桥段，最快
    dict(tag="S4", src=C("S4_bridge"), dur=3.0, mode="cut",
         vo="D4_goat", vo_at=0.15,
         note="全片最快，2.71s 台词"),

    # ⑤ 留白①：刹车特写（从 S4 尾部抽 1 秒，无台词）
    dict(tag="S4b", src=C("S4_bridge"), dur=0.9, mode="tail",
         vo=None, note="★ 留白①：动作急停，让上一镜砸下来"),

    # ⑥ 大堂
    dict(tag="S5", src=C("S5_lobby"), dur=5.0, mode="slow",
         vo="D5_lobby", vo_at=0.20,
         note="门禁对峙"),

    # ⑦ 电梯，旁白最重的一句
    dict(tag="S6", src=C("S6_elevator"), dur=3.0, mode="cut",
         vo="N6_mistake", vo_at=0.16,
         note="★ 这句话放在这里，画面和情绪咬合"),

    # ⑧ 留白②：静帧（他吸气前的一刻）
    dict(tag="S6b", src=C("S6_elevator"), dur=0.8, mode="freeze",
         vo=None, note="★ 留白②：0.8 秒完全静止，只有环境声"),

    # ⑨ 天台：两句台词 + 中间停顿
    dict(tag="S7", src=C("S7_rooftop"), dur=8.2, mode="slow_freeze",
         vo="N7_accident", vo_at=0.30, vo2="D7_tomorrow", vo2_at=5.30,
         note="★ 长镜留白：先说意外呢，停 0.5s，再说明天见"),

    # ⑩ 留白③：城市空镜收尾
    dict(tag="S8", src=os.path.join(CLIPS_KB, "S7_rooftop.mp4"), dur=3.0, mode="cut",
         vo=None, fade_out=1.2,
         note="★ 留白③：3 秒只有环境声，淡出收住"),
]


def run(args):
    r = subprocess.run([FF, "-y", "-v", "error"] + args, capture_output=True)
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


def prep_segment(seg, norm):
    """把素材整理成目标时长。
    mode:
      cut        —— 直接裁
      slow       —— 放慢到目标时长（上限 1.35x，超了补冻结）
      tail       —— 取素材最后 N 秒
      freeze     —— 取 1 帧冻住
      slow_freeze—— 先放慢到上限，再冻结补足
    """
    src, dur, mode = seg["src"], seg["dur"], seg["mode"]
    dst = os.path.join(norm, seg["tag"] + ".mp4")
    if not os.path.exists(src):
        raise RuntimeError(f"缺素材 {src}")

    sd = dur_of(src)
    vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease," \
         f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS}"
    args = ["-i", src]

    if mode == "cut":
        args += ["-t", f"{dur:.3f}", "-vf", vf]

    elif mode == "tail":
        # 取素材最后 dur 秒，用来做"急刹"
        start = max(0.0, sd - dur - 0.05)
        args = ["-ss", f"{start:.3f}", "-i", src,
                "-t", f"{dur:.3f}", "-vf", vf]

    elif mode == "freeze":
        # 取素材中间一帧，冻住 dur 秒
        mid = sd * 0.55
        args = ["-ss", f"{mid:.3f}", "-i", src,
                "-vf", vf + f",tpad=stop_mode=clone:stop_duration={dur:.3f}",
                "-t", f"{dur:.3f}"]

    elif mode in ("slow", "slow_freeze"):
        ratio = dur / sd
        ratio = min(1.35, max(1.0, ratio))
        need = dur
        vf2 = vf + f",setpts=PTS*{ratio:.4f}"
        covered = sd * ratio
        if covered < need - 0.02 and mode == "slow_freeze":
            vf2 += f",tpad=stop_mode=clone:stop_duration={need - covered + 0.3:.3f}"
        args += ["-vf", vf2, "-t", f"{need:.3f}"]

    args += ["-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
             "-pix_fmt", "yuv420p", dst]
    run(args)
    return dst, sd


def main():
    os.makedirs(OUT, exist_ok=True)
    norm = os.path.join(EP, "_norm_v3")
    os.makedirs(norm, exist_ok=True)

    with open(os.path.join(AUD, "_timeline.json"), encoding="utf-8") as f:
        TL = json.load(f)

    # ── 1. 逐段整理 ──
    segfiles, starts = [], []
    t = 0.0
    for seg in SEGMENTS:
        dst, sd = prep_segment(seg, norm)
        segfiles.append(dst)
        starts.append(t)
        ratio = seg["dur"] / sd if sd > 0 else 1
        print(f"  {seg['tag']:5s} {seg['dur']:4.1f}s  素材 {sd:4.2f}s  "
              f"{seg['mode']:11s} x{min(1.35, ratio):.2f}")
        t += seg["dur"]
    total = t
    print(f"  总长 {total:.2f}s")

    # ── 2. 拼接 ──
    lst = os.path.join(norm, "_list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for s in segfiles:
            f.write("file '%s'\n" % s.replace("\\", "/"))
    vcat = os.path.join(norm, "_vcat.mp4")
    run(["-f", "concat", "-safe", "0", "-i", lst,
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-an", vcat])
    vfix = os.path.join(norm, "_vfix.mp4")
    run(["-i", vcat, "-vf", f"fps={FPS},setpts=N/{FPS}/TB,settb=1/{FPS},setsar=1",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-an", vfix])

    # ⛔ 关键修正：total 必须用**实际拼接后的时长**，不能用设计值。
    #    上一版用设计值 39.9s 但实际只有 38.12s，
    #    淡出起点算到 38.7s —— 落在片尾之后，**淡出完全没出现**。
    real_total = dur_of(vfix)
    print(f"  实际拼接时长 {real_total:.2f}s（设计 {total:.2f}s）")
    drift = real_total - total
    total = real_total

    # ── 3. 配音 + 字幕 ──
    inputs = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    filters, mix_in, subs = [], [], []
    idx = 1
    for seg, st in zip(SEGMENTS, starts):
        for key, atkey in (("vo", "vo_at"), ("vo2", "vo2_at")):
            lid = seg.get(key)
            if not lid:
                continue
            mp3 = os.path.join(AUD, lid + ".mp3")
            if not os.path.exists(mp3):
                print(f"  ! 缺 {lid}")
                continue
            inputs += ["-i", mp3]
            ms = int((st + seg[atkey]) * 1000)
            filters.append(f"[{idx}:a]adelay={ms}|{ms}[vo{idx}]")
            mix_in.append(f"[vo{idx}]")
            idx += 1
            for row in TL.get(lid, {}).get("sentences", []):
                subs.append((round(st + seg[atkey] + row["start"], 2),
                             round(st + seg[atkey] + row["end"], 2),
                             row["text"]))

    # 环境底：按**段落**驱动，不是按硬编码时间点
    #   （上一版用固定时间点，S7 短了 1.37s 后整条曲线就错位了）
    #   每个段落一个"情绪音量"，留白处刻意压低 —— 这才是"静下来"
    BED_LEVEL = {
        "S1": 0.050, "S2": 0.062, "S3": 0.088, "S4": 0.115,
        "S4b": 0.026,          # ★ 留白①：急停，几乎只剩房间底噪
        "S5": 0.058, "S6": 0.038,
        "S6b": 0.018,          # ★ 留白②：最静的一刻
        "S7": 0.078, "S8": 0.052,
    }
    bed_pts = []
    for seg, st in zip(SEGMENTS, starts):
        lvl = BED_LEVEL.get(seg["tag"], 0.05)
        bed_pts.append((st, lvl))
        bed_pts.append((st + seg["dur"], lvl))
    # 末尾淡出
    bed_pts.append((total, 0.006))

    parts = []
    for i in range(len(bed_pts) - 1):
        (t0, a0), (t1, a1) = bed_pts[i], bed_pts[i + 1]
        span = max(0.01, t1 - t0)
        parts.append(
            f"if(between(t,{t0:.3f},{t1:.3f}),"
            f"{a0:.4f}+({a1-a0:+.4f})*(t-{t0:.3f})/{span:.3f},")
    expr = "".join(parts) + "0.05" + ")" * len(parts)

    filters.append(
        f"anoisesrc=d={total}:c=brown:a=1,lowpass=f=1300,"
        f"volume='{expr}':eval=frame,"
        f"afade=t=in:st=0:d=1.2,afade=t=out:st={max(0,total-2.0):.2f}:d=2.0[bed]")
    mix_in.append("[bed]")
    filters.append(f"{''.join(mix_in)}amix=inputs={len(mix_in)}:normalize=0:"
                   f"dropout_transition=0[mix]")
    filters.append("[mix]alimiter=limit=0.94[aout]")

    mixed = os.path.join(EP, "_mix_v3.m4a")
    run(inputs + ["-filter_complex", ";".join(filters),
                  "-map", "[aout]", "-t", f"{total:.3f}",
                  "-c:a", "aac", "-b:a", "192k", mixed])

    # ── 4. 字幕 + 淡入淡出 + 合成 ──
    subs.sort()
    ass = os.path.join(EP, "_sub_v3.ass")
    make_ass(subs, ass)
    print(f"\n  字幕 {len(subs)} 条（全部逐字稿）")
    for a, b, c in subs:
        print(f"    {a:6.2f}-{b:6.2f}  {c}")

    ass_esc = ass.replace("\\", "/").replace(":", "\\:")
    vf_final = (f"ass='{ass_esc}',"
                f"fade=t=in:st=0:d=0.5,"
                f"fade=t=out:st={total-1.2:.2f}:d=1.2")
    final = os.path.join(OUT, "骡马阿甘_EP01_v3.mp4")
    run(["-i", vfix, "-i", mixed,
         "-vf", vf_final,
         "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18",
         "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-shortest", final])

    print(f"\n✓ {final}")
    print(f"  {dur_of(final):.2f}s  {os.path.getsize(final)//1024} KB")
    with open(os.path.join(EP, "_timeline_v3.json"), "w", encoding="utf-8") as f:
        json.dump({"total": total,
                   "segments": [{k: v for k, v in s.items() if k != "src"}
                                for s in SEGMENTS],
                   "starts": starts}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
