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


def _b64(path, data_uri=False):
    """读图转 base64。
    ⚠️ 实测：Agnes 的 `extra_body.image` 要的是**纯 base64**，
       带 `data:image/png;base64,` 前缀会报
       "invalid image base64: illegal base64 data at input byte 1"。
    """
    with open(path, "rb") as f:
        raw = base64.b64encode(f.read()).decode()
    if not data_uri:
        return raw
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp"}.get(ext, "image/png")
    return f"data:{mime};base64," + raw


def _prep_images(init_images):
    """把各种形式的输入统一成 API 要的形式。
       · http(s) URL          → 原样
       · 本地文件路径（存在）  → 读成纯 base64
       · 其它字符串            → 认为已经是 base64，原样
    """
    out = []
    for im in init_images:
        if not isinstance(im, str):
            raise TypeError("图片项必须是路径 / URL / base64 字符串")
        if im.startswith(("http://", "https://")):
            out.append(im)
        elif os.path.isfile(im):
            out.append(_b64(im))
        else:
            out.append(im)
    return out


def gen_image(prompt, size="2K", ratio="1:1", negative=None, init_images=None,
              n=1, save_to=None):
    """生成图片。返回保存路径列表。"""
    body = {"model": IMG_MODEL, "prompt": prompt, "n": n, "size": size}
    extra = {"response_format": "b64_json", "ratio": ratio}
    if negative:
        extra["negative_prompt"] = negative
    if init_images:
        imgs = _prep_images(init_images)
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
    """生成视频。

    mode 与图片字段的对应（实测，传错直接 400）：
      · keyframe  → 必须带 `first_frame`（可选 `last_frame`），单张
                    报错："keyframe 模式需要 first_frame 或 last_frame"
      · reference → 带 `images` 列表（保角色身份）
      · text      → 不带图
    """
    body = {"model": VID_MODEL, "mode": mode, "prompt": prompt,
            "seconds": str(seconds), "size": "720P", "aspect_ratio": ratio, "n": 1}
    if images:
        prepped = _prep_images(list(images))
        if mode == "keyframe":
            body["first_frame"] = prepped[0]
            if len(prepped) > 1:
                body["last_frame"] = prepped[1]
        elif mode == "reference":
            body["images"] = prepped
        else:
            raise ValueError(f"mode={mode} 不接受图片")
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
