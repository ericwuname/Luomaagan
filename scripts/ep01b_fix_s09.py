#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
补拍 S09 —— 下载中断（IncompleteRead）导致丢失的关键镜

S09 是全片转折：他在窗外看别人过生日。
必须补上，否则故事断在这里。

⚠️ 网络中断是偶发的。加固措施：
   · 下载失败自动重试 3 次（带退避）
   · 每次重试前删掉残缺文件，避免被当成"已存在"跳过
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agnes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.join(ROOT, "work", "ep01b")
CLIPS = os.path.join(EP, "clips")
NAME = "S09_window"
SEC = "7"

MOTION = (
 "**THE CAMERA PUSHES IN VERY SLOWLY** toward the lit ground-floor window, so the warm "
 "rectangle of light grows in frame and the dark street at the edges shrinks. It only pushes "
 "in, never pulls back. Inside the window a family leans over a birthday cake, laughing "
 "and singing, balloons taped to the glass sway slightly, the candles flicker. "
 "He sits on his scooter in the dark street, watching, not moving, his ears slack.")

if __name__ == "__main__":
    img = os.path.join(EP, NAME + ".png")
    out = os.path.join(CLIPS, NAME + ".mp4")
    assert os.path.exists(img), f"缺首帧 {img}"

    for attempt in range(3):
        if os.path.exists(out):
            os.remove(out)          # 删残缺文件，防止被跳过
        print(f"  第 {attempt+1} 次 ...", flush=True)
        try:
            t0 = time.time()
            agnes.gen_video(MOTION, seconds=SEC, mode="keyframe",
                            images=[img], ratio="16:9", save_to=out)
            dt = time.time() - t0
            # 校验完整性
            import subprocess
            FF = (r"C:/Users/87465/.workbuddy/binaries/python/envs/aitv/Lib/"
                  r"site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe")
            r = subprocess.run([FF, "-v", "error", "-i", out, "-f", "null", "-"],
                               capture_output=True)
            if r.stderr.strip():
                raise RuntimeError("文件校验失败: " + r.stderr.decode("utf-8", "ignore")[:100])
            with open(out + ".motion.txt", "w", encoding="utf-8") as f:
                json.dump({"seconds": SEC, "motion": MOTION,
                           "elapsed_s": round(dt, 1)}, f, ensure_ascii=False, indent=2)
            print(f"    ✓ {dt:.0f}s  {os.path.getsize(out)//1024} KB", flush=True)
            break
        except Exception as e:
            print(f"    ✗ {str(e)[:160]}", flush=True)
            time.sleep(5 * (attempt + 1))
