#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
EP02《别敲门，鹦鹉会替你》· 剪辑

18 镜 / 约 108 秒

⛔ 这一集是喜剧，**声音的"静 → 响"对比就是节奏本身**：
   · 03–07 小声配送段：环境底压到极低（-46dB），只留蹄声、衣料、袋子轻触
   · 08 第一声门铃：突然炸开，是全片第一个爆点
   · 11/13 升级：鹦鹉一次比一次响
   · 18 收尾：三声门轴响，让观众"听到"整层楼开门
     （门缝里那双眼睛两次都没生成出来，改用声音解决，见 docs/15 §3.2）

门铃音效复用同一条 `bell.mp3`（08 和 16 用同一个音色），
这是剧本 F 节的要求：全片门铃动机必须一致。
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep02")
CLIPS = os.path.join(EP, "clips")
AUD = os.path.join(EP, "audio")
B = os.path.join(ROOT, "work", "ep01b", "clips")   # 复用素材
OUT = os.path.join(ROOT, "release")
FF = (r"C:/Users/87465/.workbuddy/binaries/python/envs/aitv/Lib/"
      r"site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe")

W, H, FPS = 1280, 704, 24

# 镜号, 素材, 目标秒, 环境音量, [(配音id, 段内起点)], 门铃音(段内起点), 说明
TIMELINE = [
 ("01_note",     os.path.join(CLIPS, "01_phone_note.mp4"), 6.0, 0.030, [], None, "手机备注（程序渲染）"),
 ("02_read",     os.path.join(CLIPS, "02_read.mp4"),       6.0, 0.062, [("D01", 0.80), ("D01b", 3.60)], None, "读备注 + 静音 + 噤声"),
 ("03_corridor", os.path.join(B, "S03_door.mp4"),          6.5, 0.026, [], None, "空楼道（复用 ep01b S03）"),
 ("04_tiptoe",   os.path.join(CLIPS, "04_tiptoe.mp4"),     6.0, 0.022, [], None, "踮脚走过（极静）"),
 ("05_bell",     os.path.join(CLIPS, "05_bell_A.mp4"),     5.0, 0.020, [], None, "★蹄手悬停（证据镜）"),
 ("06_sees",     os.path.join(CLIPS, "06_parrot_sees.mp4"), 5.0, 0.030, [], None, "鹦鹉看到阿甘"),
 ("07_bag",      os.path.join(CLIPS, "07_bag.mp4"),        6.0, 0.022, [], None, "放袋子（极静）"),
 ("08_bell",     os.path.join(CLIPS, "08_parrot_bell.mp4"), 6.0, 0.034, [("D02", 0.90)], 0.90, "★第一声门铃（爆点）"),
 ("09_shock",    os.path.join(CLIPS, "09_shock.mp4"),      5.0, 0.028, [("D03", 1.40)], None, "阿甘惊住"),
 ("10_rabbit",   os.path.join(CLIPS, "10_rabbit_call.mp4"), 6.0, 0.030, [("D04", 1.00)], None, "兔子开会"),
 ("11_mimic",    os.path.join(CLIPS, "11_parrot_mimic.mp4"), 6.0, 0.036, [("D05", 1.10)], None, "★第一次放大"),
 ("12_whisper",  os.path.join(CLIPS, "12_whisper.mp4"),    6.0, 0.020, [("D06", 1.40)], None, "阿甘低语（极轻）"),
 ("13_loud",     os.path.join(CLIPS, "13_parrot_loud.mp4"), 5.0, 0.040, [("D07", 1.00)], None, "★第二次放大"),
 ("14_door",     os.path.join(CLIPS, "14_door_open_B.mp4"), 7.0, 0.030, [("D08", 1.60)], None, "开门，兔子误会"),
 ("15_evidence", os.path.join(CLIPS, "15_silent.mp4"),     6.0, 0.028, [("D09", 1.50)], None, "★证据（程序渲染静音界面）"),
 ("16_triangle", os.path.join(CLIPS, "16_triangle.mp4"),   6.0, 0.034, [("D10", 1.00)], 1.00, "★三人 + 五星好评"),
 ("17_fivestar", os.path.join(CLIPS, "17_fivestar.mp4"),   6.0, 0.030, [("D11", 1.10)], None, "五星 + 道歉"),
 ("18_neighbors", os.path.join(CLIPS, "18_neighbors_B.mp4"), 7.0, 0.032, [("D12", 4.20)], None, "★整层楼（靠门轴声）"),
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


def make_hinge(path, sr=24000):
    """合成"门轴吱呀"：噪声 + 带通 + 缓慢滑频，短促 0.5s"""
    import numpy as np
    n = int(0.55 * sr)
    t = np.arange(n) / sr
    noise = np.random.RandomState(7).randn(n)
    # 简单带通（用差分近似）
    env = np.exp(-t * 5.5) * (1 - np.exp(-t * 60))
    sig = noise * env * 0.9
    # 加一个低频滑动音
    f = np.linspace(420, 180, n)
    tone = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 6) * 0.35
    sig = np.clip((sig * 0.5 + tone), -1, 1) * 0.45
    pcm = (sig * 32767).astype("<i2").tobytes()
    subprocess.run([FF, "-y", "-v", "error", "-f", "s16le", "-ar", str(sr), "-ac", "1",
                    "-i", "-", "-c:a", "libmp3lame", "-b:a", "192k", path],
                   input=pcm, check=True)
    return path


def main():
    os.makedirs(OUT, exist_ok=True)
    norm = os.path.join(EP, "_norm")
    os.makedirs(norm, exist_ok=True)

    tl_path = os.path.join(AUD, "_timeline.json")
    TL = {}
    if os.path.exists(tl_path):
        with open(tl_path, encoding="utf-8") as f:
            TL = json.load(f)

    # ── 1. 每段整理到目标时长 ──
    segs, starts, t = [], [], 0.0
    for name, src, target, lvl, vos, bell, note in TIMELINE:
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
        else:
            run(["-i", src, "-t", f"{target:.3f}", "-vf", vf, "-an",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                 "-pix_fmt", "yuv420p", dst])
        segs.append(dst)
        starts.append(t)
        t += target
        print(f"  {name:14s} {sd:5.2f}→{target:4.1f}s  {note}")
    total_design = t
    print(f"  设计总长 {total_design:.2f}s")

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

    total = dur_of(vfix)     # ⛔ 必须用实测值，否则淡出会落在片尾之后
    print(f"  实际拼接 {total:.2f}s")

    # ── 3. 配音 + 门铃 + 门轴 + 环境 ──
    inputs = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    filters, mix_in, subs = [], [], []
    idx = 1

    bell_path = os.path.join(AUD, "bell.mp3")
    hinge_path = make_hinge(os.path.join(AUD, "hinge.mp3"))

    for (name, src, target, lvl, vos, bell_at, note), st in zip(TIMELINE, starts):
        for lid, at in vos:
            mp3 = os.path.join(AUD, lid + ".m4a")
            if not os.path.exists(mp3):
                continue
            inputs += ["-i", mp3]
            ms = int((st + at) * 1000)
            filters.append(f"[{idx}:a]adelay={ms}|{ms}[vo{idx}]")
            mix_in.append(f"[vo{idx}]")
            idx += 1
            # ⛔ 不能按 edge-tts 的句边界逐句出字幕 ——
            #    它会按感叹号切，导致"嘘！""我在开会！"各自跳一条，观众看着累。
            #    改成**一条台词一条字幕**，时间取首句起点到末句终点。
            rows = TL.get(lid, {}).get("sentences", [])
            if rows:
                a = st + at + rows[0]["start"]
                b = st + at + rows[-1]["end"]
                text = "".join(r["text"] for r in rows)
                subs.append((round(a, 2), round(b, 2), text))
        # 门铃音效（08 / 16 共用同一音色）
        if bell_at is not None and os.path.exists(bell_path):
            inputs += ["-i", bell_path]
            ms = int((st + bell_at) * 1000)
            filters.append(f"[{idx}:a]adelay={ms}|{ms},volume=0.85[bl{idx}]")
            mix_in.append(f"[bl{idx}]")
            idx += 1

    # 18 镜：三声门轴响，让观众"听到"整层楼开门
    n18_st = starts[-1] if starts else 0
    for k, off in enumerate((1.1, 2.4, 3.6)):
        inputs += ["-i", hinge_path]
        ms = int((n18_st + off) * 1000)
        filters.append(f"[{idx}:a]adelay={ms}|{ms},volume={0.55 - k*0.10:.2f},"
                       f"highpass=f=180[hg{idx}]")
        mix_in.append(f"[hg{idx}]")
        idx += 1

    # BGM（音乐本身已有段落起伏：小声段"蹑手蹑脚"、门铃处"提起来"）
    # ⛔ 第一版只给了固定音量 0.78，结果把"静"垫高了：小声段从 -49 抬到 -38，
    #    门铃仍是 -25，**落差从 24dB 压到 13dB，冲击力弱了**。
    #    → 音乐要会"让路"：小声段压到 0.24，爆点放到 1.0。
    bgm = os.path.join(EP, "bgm_EP02.m4a")
    if os.path.exists(bgm):
        inputs += ["-i", bgm]
        BGM_LVL = {
            "01_note": 0.90, "02_read": 0.82, "03_corridor": 0.50,
            "04_tiptoe": 0.26, "05_bell": 0.22, "06_sees": 0.32, "07_bag": 0.22,
            "08_bell": 1.00, "09_shock": 0.58, "10_rabbit": 0.52,
            "11_mimic": 0.88, "12_whisper": 0.22, "13_loud": 0.95,
            "14_door": 0.58, "15_evidence": 0.50, "16_triangle": 0.92,
            "17_fivestar": 0.68, "18_neighbors": 1.00,
        }
        bp = []
        for (name, src, target, lvl, vos, bell_at, note), st in zip(TIMELINE, starts):
            v = BGM_LVL.get(name, 0.70)
            bp.append((st, v))
            bp.append((st + target, v))
        bp.append((total, 0.02))
        parts2 = []
        for i in range(len(bp) - 1):
            (t0, a0), (t1, a1) = bp[i], bp[i + 1]
            span = max(0.01, t1 - t0)
            parts2.append(f"if(between(t,{t0:.3f},{t1:.3f}),"
                          f"{a0:.4f}+({a1-a0:+.4f})*(t-{t0:.3f})/{span:.3f},")
        expr2 = "".join(parts2) + "0.70" + ")" * len(parts2)
        filters.append(f"[{idx}:a]volume='0.80*({expr2})':eval=frame,"
                       f"atrim=0:{total:.3f},"
                       f"afade=t=in:st=0:d=1.0[bgm]")
        mix_in.append("[bgm]")
        idx += 1
        print("  BGM 已并入（带段落让路曲线）")

    # 环境底：按段落（小声段压到极低，笑点段抬高）
    bed_pts = []
    for (name, src, target, lvl, vos, bell_at, note), st in zip(TIMELINE, starts):
        bed_pts.append((st, lvl))
        bed_pts.append((st + target, lvl))
    bed_pts.append((total, 0.004))
    parts = []
    for i in range(len(bed_pts) - 1):
        (t0, a0), (t1, a1) = bed_pts[i], bed_pts[i + 1]
        span = max(0.01, t1 - t0)
        parts.append(f"if(between(t,{t0:.3f},{t1:.3f}),"
                     f"{a0:.4f}+({a1-a0:+.4f})*(t-{t0:.3f})/{span:.3f},")
    expr = "".join(parts) + "0.04" + ")" * len(parts)

    filters.append(
        f"anoisesrc=d={total}:c=brown:a=1,lowpass=f=1400,"
        f"volume='{expr}':eval=frame,"
        f"afade=t=in:st=0:d=1.0,afade=t=out:st={max(0,total-1.8):.2f}:d=1.8[bed]")
    mix_in.append("[bed]")
    filters.append(f"{''.join(mix_in)}amix=inputs={len(mix_in)}:normalize=0:"
                   f"dropout_transition=0[mix]")
    filters.append("[mix]alimiter=limit=0.94[aout]")

    mixed = os.path.join(EP, "_mix.m4a")
    run(inputs + ["-filter_complex", ";".join(filters),
                  "-map", "[aout]", "-t", f"{total:.3f}",
                  "-c:a", "aac", "-b:a", "192k", mixed])

    # ── 4. 字幕 + 合成 ──
    subs.sort()
    ass = os.path.join(EP, "_sub.ass")
    make_ass(subs, ass)
    print(f"\n  字幕 {len(subs)} 条")
    for a, b, c in subs:
        print(f"    {a:6.2f}-{b:6.2f}  {c}")

    ass_esc = ass.replace("\\", "/").replace(":", "\\:")
    vf_final = (f"ass='{ass_esc}',fade=t=in:st=0:d=0.5,"
                f"fade=t=out:st={max(0,total-1.4):.2f}:d=1.4")
    final = os.path.join(OUT, "骡马阿甘_EP02_别敲门鹦鹉会替你.mp4")
    run(["-i", vfix, "-i", mixed, "-vf", vf_final,
         "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-shortest", final])

    print(f"\n✓ {final}")
    print(f"  {dur_of(final):.2f}s  {os.path.getsize(final)//1024} KB")


if __name__ == "__main__":
    main()
