#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
BGM 合成器 —— 用 numpy 从零合成配乐

⛔ 为什么自己做
   两集成片都没有 BGM，只有环境噪。**喜剧尤其需要音乐来"托"笑点**：
   笑点前的停顿要有音乐"悬住"，笑点砸下来要有音乐"接住"。
   这是"呼吸感"的另一半。

   不占视频配额，纯程序生成，可精确编排到秒。

✅ 设计原则（一条）：**音乐跟着情绪曲线走，不铺一条到底。**
   · 该停的地方真停（比如 EP01 台阶插火柴，只剩单音）
   · 该憋的地方憋（EP02 小声配送段，音乐蹑手蹑脚）
   · 该炸的地方炸（门铃响，音乐跟着一提）

音色都是纯合成：
   钢琴   = 多谐波叠加 + 各自衰减率 + 轻微失谐
   拨弦   = 锯齿波 + 快速低通扫频 + 极短衰减
   木琴   = 高频正弦 + 二次谐波 + 极快衰减 + 起音噪声
   混响   = 并联梳状延迟 + 全通滤波（Schroeder 简易版）
"""
import math
import os
import subprocess

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
FF = (r"C:/Users/87465/.workbuddy/binaries/python/envs/aitv/Lib/"
      r"site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe")

# ── 音高表 ──
NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
        "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10,
        "Bb": 10, "B": 11}


def hz(name, octave=4):
    """'C' + 4 → 261.63"""
    return 440.0 * (2 ** ((NOTE[name] + (octave - 4) * 12 - 9) / 12.0))


def env_adsr(n, a=0.01, d=0.1, s=0.6, r=0.3, sr=SR):
    a_n, d_n, r_n = int(a * sr), int(d * sr), int(r * sr)
    s_n = max(0, n - a_n - d_n - r_n)
    parts = [
        np.linspace(0, 1, a_n, endpoint=False) if a_n else np.array([]),
        np.linspace(1, s, d_n, endpoint=False) if d_n else np.array([]),
        np.full(s_n, s),
        np.linspace(s, 0, r_n) if r_n else np.array([]),
    ]
    e = np.concatenate([p for p in parts if len(p)])
    if len(e) < n:
        e = np.pad(e, (0, n - len(e)))
    return e[:n]


# ─────────────────────────── 音色 ───────────────────────────
def piano(f, dur, vel=0.7):
    """多谐波 + 各自衰减率：高次谐波衰减更快，这是钢琴的物理特征"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    HAR = [(1, 1.00, 2.2), (2, 0.42, 3.0), (3, 0.20, 4.2),
           (4.2, 0.10, 5.5), (5.4, 0.05, 7.0)]   # (倍频, 幅度, 衰减速度)
    for mul, amp, dec in HAR:
        det = 1.0 + (np.random.RandomState(int(f) % 97 + int(mul * 10)).randn() * 0.0008)
        sig += amp * np.sin(2 * np.pi * f * mul * det * t) * np.exp(-t * dec)
    # 敲击瞬态
    att = np.exp(-t * 90) * np.random.RandomState(3).randn(n) * 0.05
    sig = (sig + att) * env_adsr(n, 0.004, 0.02, 0.32, min(0.6, dur * 0.5))
    return sig * vel


def pizz(f, dur, vel=0.7):
    """拨弦：锯齿波 + 快速低通扫频"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    # 近似锯齿（多个谐波，幅度 1/k）
    sig = np.zeros(n)
    for k in range(1, 13):
        if f * k > SR / 2.2:
            break
        sig += (1.0 / k) * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (6 + k * 1.8))
    sig *= env_adsr(n, 0.002, 0.05, 0.18, min(0.35, dur * 0.6))
    return sig * vel * 0.55


def xyl(f, dur, vel=0.7):
    """木琴：高频正弦 + 二次谐波 + 极快衰减 + 起音噪声"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * f * t) * np.exp(-t * 11) +
           np.sin(2 * np.pi * f * 3.02 * t) * 0.35 * np.exp(-t * 20) +
           np.sin(2 * np.pi * f * 5.1 * t) * 0.12 * np.exp(-t * 30))
    click = np.random.RandomState(int(f) % 89).randn(n) * np.exp(-t * 400) * 0.25
    sig = (sig + click) * env_adsr(n, 0.001, 0.01, 0.10, min(0.25, dur * 0.5))
    return sig * vel * 0.5


VOICES = {"piano": piano, "pizz": pizz, "xyl": xyl}


def pad(freqs, dur, vel=0.16):
    """持续和弦铺底 —— 这一层是为了**填满空隙**，不让音乐出现数字静音。

    ⛔ 教训：只用钢琴/拨弦/木琴这类短音色，音符衰减完就是 -100dB 的死寂，
       整条 BGM 会变成"叮…静…叮…静"，听起来像音频坏了。
       电影配乐的标准做法是**pad 铺底 + 主奏在上**，这里补上 pad。
    """
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for f in freqs:
        for det in (0.997, 1.003):        # 轻微失谐 → 合唱感，不呆板
            sig += np.sin(2 * np.pi * f * det * t)
    sig /= max(1, len(freqs) * 2)
    sig *= env_adsr(n, 0.30, 0.25, 0.72, 0.55)   # 慢起慢落
    return sig * vel


# ─────────────────────────── 混响 ───────────────────────────
def reverb(x, mix=0.28, decay=0.55, size=0.055):
    """Schroeder 简易混响：4 梳状 + 2 全通"""
    if mix <= 0:
        return x
    d = int(size * SR)
    combs = []
    for off in (d, int(d * 1.19), int(d * 1.41), int(d * 1.63)):
        y = np.zeros(len(x) + off)
        y[:len(x)] = x
        for i in range(off, len(y)):
            y[i] += y[i - off] * decay
        combs.append(y[:len(x)])
    wet = np.mean(combs, axis=0)
    # 全通（轻微扩散）
    for off in (int(d * 0.31), int(d * 0.53)):
        if off < 2:
            continue
        y = wet.copy()
        for i in range(off, len(y)):
            y[i] = -0.5 * y[i] + wet[i - off] + 0.5 * y[i - off]
        wet = y
    return (1 - mix) * x + mix * wet


# ─────────────────────────── 编排 ───────────────────────────
def build(score, total, out_wav):
    """score: [(start, end, voice, vel, pattern)] —— pattern 决定和弦节奏"""
    buf = np.zeros(int(total * SR) + SR)

    bpm = score["bpm"]
    beat = 60.0 / bpm
    bar = beat * 4
    chords = score["chords"]

    # ── 第一层：pad 铺底（贯穿全曲，首尾交叠，避免出现死寂）──
    pad_lvl = score.get("pad", 0.15)
    ci, t = 0, 0.0
    while t < total:
        chord = chords[ci % len(chords)]
        ci += 1
        freqs = [hz(n, o) for (n, o) in chord]
        d = min(bar * 1.2, total - t + 0.45)     # 稍长，和下一段交叠 0.45s
        s = pad(freqs, d, pad_lvl)
        i = int(t * SR)
        buf[i:i + len(s)] += s
        t += bar

    # ── 第二层：主奏 ──
    for (t0, t1, voice, vel, pattern) in score["sections"]:
        if voice is None or t1 <= t0:
            continue
        fn = VOICES[voice]
        t = t0
        ci = 0
        while t < t1 - 0.01:
            chord = chords[ci % len(chords)]
            ci += 1
            if pattern == "arp":            # 分解和弦（8 分音符）
                seq = chord + [chord[1]] + chord[::-1][:2]
                step = beat / 2
                for k, (nm, oc) in enumerate(seq):
                    tt = t + k * step
                    if tt >= t1:
                        break
                    dur = min(step * 1.6, t1 - tt)
                    s = fn(hz(nm, oc), dur, vel)
                    i = int(tt * SR)
                    buf[i:i + len(s)] += s
            elif pattern == "block":        # 柱式和弦（每拍）
                for b in range(4):
                    tt = t + b * beat
                    if tt >= t1:
                        break
                    for (nm, oc) in chord:
                        dur = min(beat * 0.85, t1 - tt)
                        s = fn(hz(nm, oc), dur, vel * 0.62)
                        i = int(tt * SR)
                        buf[i:i + len(s)] += s
            elif pattern == "single":
                # ⛔ 原来这里"每小节只弹一个音"，音符衰减后就是数字静音（-180dB），
                #    实测听感像音频坏了。改成**持续低音铺底 + 稀疏点缀**：
                #    低音用小节长度的长音填满，上面只放两个高音点。
                nm, oc = chord[0]
                low_pad = fn(hz(nm, oc - 1), bar * 0.99, vel * 0.72)
                i = int(t * SR)
                buf[i:i + len(low_pad)] += low_pad
                for b in (0, 2):
                    tt = t + b * beat
                    if tt >= t1:
                        break
                    nm2, oc2 = chord[-1]
                    s2 = fn(hz(nm2, oc2 + 1), beat * 1.15, vel * 0.45)
                    i2 = int(tt * SR)
                    buf[i2:i2 + len(s2)] += s2
            t += bar

    buf = reverb(buf, mix=score.get("reverb", 0.26))
    # 归一化到 -20 dBFS 附近
    peak = np.max(np.abs(buf)) + 1e-9
    buf = buf / peak * score.get("peak", 0.30)
    # 首尾淡入淡出
    fi, fo = int(0.8 * SR), int(1.6 * SR)
    buf[:fi] *= np.linspace(0, 1, fi)
    buf[-fo:] *= np.linspace(1, 0, fo)
    pcm = (np.clip(buf, -1, 1) * 32767).astype("<i2")
    stereo = np.stack([pcm, pcm], axis=1).reshape(-1)
    subprocess.run([FF, "-y", "-v", "error", "-f", "s16le", "-ar", str(SR),
                    "-ac", "2", "-i", "-", "-c:a", "aac", "-b:a", "192k", out_wav],
                   input=stereo.tobytes(), check=True)
    return out_wav


# ─────────────────────────── 两集的谱 ───────────────────────────
# EP01《第一万单》：c 小调偏温暖的大调，慢，前半孤寂，后半暖
EP01 = {
 "bpm": 66,
 "chords": [[("C", 4), ("E", 4), ("G", 4)],
            [("G", 3), ("B", 3), ("D", 4)],
            [("A", 3), ("C", 4), ("E", 4)],
            [("F", 3), ("A", 3), ("C", 4)]],
 "reverb": 0.32,
 "peak": 0.26,
 "sections": [
   # (起, 止, 音色, 力度, 织体)
   (0.0,   12.0,  "piano", 0.55, "single"),   # 出租屋：独处
   (12.0,  24.0,  "piano", 0.62, "arp"),      # 镜子/出门
   (24.0,  46.0,  "pizz",  0.55, "arp"),      # 送单：轻快
   (46.0,  60.0,  "piano", 0.45, "single"),   # 门关上：落
   (60.0,  72.0,  "piano", 0.50, "arp"),      # 隔窗看：向往
   (72.0,  92.0,  "piano", 0.68, "arp"),      # 开门/塞蛋糕：暖
   (92.0, 101.0,  "piano", 0.50, "single"),   # 台阶：只剩单音
   (101.0, 106.5, "piano", 0.60, "block"),    # 城市：收
 ],
}

# EP02《别敲门》：轻快俏皮，小声段蹑手蹑脚，门铃处一炸
EP02 = {
 "bpm": 112,
 "chords": [[("C", 4), ("E", 4), ("G", 4)],
            [("A", 3), ("C", 4), ("E", 4)],
            [("F", 3), ("A", 3), ("C", 4)],
            [("G", 3), ("B", 3), ("D", 4)]],
 "reverb": 0.20,
 "peak": 0.30,
 "sections": [
   (0.0,   12.0,  "xyl",   0.60, "arp"),      # 接单：俏皮
   (12.0,  18.5,  "pizz",  0.55, "arp"),      # 进楼
   (18.5,  40.5,  "pizz",  0.30, "single"),   # ★小声配送段：蹑手蹑脚
   (40.5,  46.5,  "xyl",   0.72, "block"),    # ★门铃爆点：提起来
   (46.5,  64.0,  "pizz",  0.45, "arp"),      # 升级
   (64.0,  70.5,  "pizz",  0.28, "single"),   # ★第二次憋着
   (70.5,  82.0,  "xyl",   0.68, "block"),    # 再炸
   (82.0,  94.0,  "pizz",  0.55, "arp"),      # 误会解开
   (94.0, 101.0,  "xyl",   0.62, "arp"),      # 五星
   (101.0, 106.5, "xyl",   0.70, "block"),    # ★整层楼：欢快收
 ],
}

if __name__ == "__main__":
    for name, sc, total in (("EP01", EP01, 106.5), ("EP02", EP02, 106.5)):
        dst_dir = os.path.join(ROOT, "work", "ep01c" if name == "EP01" else "ep02")
        os.makedirs(dst_dir, exist_ok=True)
        out = os.path.join(dst_dir, f"bgm_{name}.m4a")
        build(sc, total, out)
        print(f"  ✓ {name}  {sc['bpm']}bpm  {os.path.getsize(out)//1024} KB  → {out}")
