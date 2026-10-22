#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
Agnes API 封装 —— 从《走蛟》项目验证过的调用方式

⛔ 密钥不写进代码！
   本文件从环境变量 AGNES_API_KEY 读取，或在项目根目录放一个 .env 文件：
       AGNES_API_KEY=cpk-xxxxxxxx
   .env 已在 .gitignore 里，不会进仓库。
   这是给多人/多 AI 协作准备的——任何人都能读代码，但拿不到别人的密钥。

实测要点（血泪，勿改）：
  · 图像：POST /v1/images/generations，model=agnes-image-2.5-flash
    `response_format` 必须放 extra_body 内，否则静默失效
    size=1K/2K/3K/4K + ratio=1:1/16:9/9:16/4:3...
    图生图输入放 extra_body.image（base64 的 data URI）
  · **文生图队列不支持 negative_prompt**，传了直接 400
  · `mode` 只能是 text / keyframe / reference，传别的 400
  · 视频 URL 在轮询返回的顶层 `url`，不在 metadata.url
  · 轮询偶发缺 status 字段，要容忍
  · 并发轮询必 429，必须串行 + 退避
"""
import base64
import json
import os
import time
import urllib.error
import urllib.request


def _load_key():
    """优先级：环境变量 > 项目根目录 .env"""
    k = os.environ.get("AGNES_API_KEY", "").strip()
    if k:
        return k
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (os.path.join(here, ".env"),
                 os.path.join(os.path.dirname(here), ".env")):
        if os.path.isfile(cand):
            with open(cand, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("AGNES_API_KEY"):
                        _, _, v = line.partition("=")
                        return v.strip().strip('"').strip("'")
    raise SystemExit(
        "缺少 AGNES_API_KEY。\n"
        "  方式一：设置环境变量 AGNES_API_KEY\n"
        "  方式二：在项目根目录建 .env，写一行 AGNES_API_KEY=你的key\n"
        "（.env 已被 .gitignore 忽略，不会进仓库）"
    )


KEY = _load_key()
BASE = "https://api.agnes-ai.cn/v1"
POLL = "https://api.agnes-ai.cn/agnesapi"
IMG_MODEL = "agnes-image-2.5-flash"
VID_MODEL = "agnes-video-2.5-flash"
TXT_MODEL = "agnes-3.0-flash"


def _req(url, body=None, retries=6, timeout=240):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    last = None
    for i in range(retries):
        req = urllib.request.Request(
            url, data=data,
            headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 429:
                time.sleep(20 * (i + 1))
                continue
            detail = ""
            try:
                detail = e.read().decode("utf-8", "ignore")[:300]
            except Exception:
                pass
            raise RuntimeError(f"HTTP {e.code}: {detail}") from None
        except Exception as e:
            last = e
            time.sleep(6 * (i + 1))
    raise RuntimeError(f"重试耗尽: {last}")


def _b64(path):
    with open(path, "rb") as f:
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                "webp": "image/webp"}.get(ext, "image/png")
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def gen_image(prompt, size="2K", ratio="1:1", negative=None, init_images=None,
              n=1, save_to=None):
    """生成图片。返回保存路径列表。"""
    body = {"model": IMG_MODEL, "prompt": prompt, "n": n, "size": size}
    extra = {"response_format": "b64_json", "ratio": ratio}
    if negative:
        extra["negative_prompt"] = negative
    if init_images:
        imgs = [im if isinstance(im, str) else _b64(im) for im in init_images]
        extra["image"] = imgs if len(imgs) > 1 else imgs[0]
    body["extra_body"] = extra

    d = _req(BASE + "/images/generations", body)
    items = d.get("data") or []
    if not items:
        raise RuntimeError("返回无 data: " + json.dumps(d, ensure_ascii=False)[:300])

    paths = []
    ts = time.strftime("%Y%m%d_%H%M%S")
    for i, it in enumerate(items):
        if it.get("b64_json"):
            raw = base64.b64decode(it["b64_json"])
        elif it.get("url"):
            with urllib.request.urlopen(it["url"], timeout=180) as r:
                raw = r.read()
        else:
            continue
        if save_to:
            p = save_to if n == 1 else save_to.replace(".png", f"_{i+1}.png")
        else:
            p = f"img_{ts}_{i}.png"
        os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        with open(p, "wb") as f:
            f.write(raw)
        paths.append(p)
    return paths


def gen_video(prompt, seconds="5", mode="keyframe", images=None, ratio="16:9",
              save_to=None):
    """生成视频。mode: text / keyframe / reference（reference 保身份，传 images 列表）"""
    body = {"model": VID_MODEL, "mode": mode, "prompt": prompt,
            "seconds": str(seconds), "size": "720P", "aspect_ratio": ratio, "n": 1}
    if images:
        body["images"] = [im if isinstance(im, str) else _b64(im) for im in images]
    d = _req(BASE + "/videos", body)
    vid = d.get("video_id") or d.get("id")
    if not vid:
        raise RuntimeError("无 video_id: " + json.dumps(d, ensure_ascii=False)[:300])

    url = None
    for _ in range(220):
        st = _req(f"{POLL}?video_id={vid}&model_name={VID_MODEL}")
        s = st.get("status", "")
        if s in ("succeed", "succeeded", "completed", "success"):
            url = st.get("url") or (st.get("metadata") or {}).get("url")
            break
        if s in ("failed", "error"):
            raise RuntimeError("视频生成失败: " + json.dumps(st, ensure_ascii=False)[:300])
        time.sleep(6)
    if not url:
        raise RuntimeError("轮询超时 / 无 url")

    with urllib.request.urlopen(url, timeout=300) as r:
        raw = r.read()
    p = save_to or f"vid_{vid}.mp4"
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    with open(p, "wb") as f:
        f.write(raw)
    return p


def chat(prompt, system=None, max_tokens=2000):
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    d = _req(BASE + "/chat/completions",
             {"model": TXT_MODEL, "messages": msgs, "max_tokens": max_tokens})
    return d["choices"][0]["message"]["content"]


if __name__ == "__main__":
    print("Agnes API 封装自检")
    try:
        print("文本:", chat("只回两个字：正常")[:20])
    except Exception as e:
        print("文本失败:", e)
