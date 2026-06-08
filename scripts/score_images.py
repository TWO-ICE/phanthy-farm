#!/usr/bin/env python3
"""
对 sources/raw/{item_id}/ 中的候选图打分，选 Top-3。
配合 fetch_rss.py 的下一步使用。

用法:
  python3 score_images.py --agent-slug linajie --item-id 3565048078-2247496419_1
"""
import argparse, os, sys, json, hashlib
from pathlib import Path
from urllib.parse import urlparse

try:
    from PIL import Image
    import imagehash
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

FARM_ROOT = Path(os.path.expanduser("~/phanthy-farm"))

# 硬过滤规则
EXCLUDE_PATTERNS = [
    ("二维码", lambda u: any(k in u.lower() for k in ["qrcode", "qr_noroaming", "biz_qr", "mmbiz_qrcode"])),
    ("公众号名片", lambda u: any(k in u.lower() for k in ["biz_head", "headimg"])),
    ("追踪像素", lambda u: False),  # 在打分时结合 width/height 判
    ("水印占位", lambda u: any(k in u.lower() for k in ["placeholder", "watermark", "default"])),
    ("显式广告", lambda u: False),  # 在 alt 中判
]

def exclude_reason(img: dict) -> str | None:
    u = img["url"].lower()
    alt = (img.get("alt") or "").lower()
    for name, fn in EXCLUDE_PATTERNS:
        if fn(u): return name
    w, h = img.get("width"), img.get("height")
    if w and h:
        if w < 200 or h < 200: return "小尺寸(<200)"
        if w <= 1 or h <= 1: return "追踪像素"
    if u.endswith(".gif"): return "GIF表情"
    if "广告" in alt or "ad" in alt or "banner" in alt: return "广告图"
    return None

def score(img: dict, position: int, cover_url: str = "") -> int:
    s = 0
    u = img["url"].lower()
    w, h = img.get("width"), img.get("height")
    if w and h:
        if w >= 600 and h >= 400: s += 3
        ratio = w / h if h else 0
        if any(abs(ratio - r) < 0.15 * r for r in [16/9, 4/3, 1.0, 3/2]):
            s += 2
    if "mmbiz_jpg" in u or "mmbiz_png" in u: s += 1
    if position >= 1: s += 1   # 第 2 段之后
    if cover_url and urlparse(img["url"]).path == urlparse(cover_url).path:
        return -1  # 与封面同源
    if img.get("alt") and "广告" not in img["alt"]: s += 1
    if any(k in u for k in ["640", "article", "content"]): s += 1
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent-slug", required=True)
    ap.add_argument("--item-id", required=True)
    args = ap.parse_args()

    md_path = FARM_ROOT / "agents" / args.agent_slug / "sources" / "raw" / f"{args.item_id}.md"
    if not md_path.exists():
        print(f"❌ 找不到 {md_path}", file=sys.stderr); sys.exit(1)

    # 读 frontmatter
    text = md_path.read_text()
    fm_lines = []
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        fm_lines = [l for l in fm.strip().split("\n") if l.strip()]
    fm = {}
    for l in fm_lines:
        if ":" in l:
            k, v = l.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')

    cover_url = fm.get("cover_url", "")
    images = []
    # 重新解析（这里简化，实际可改 fetch_rss 把 images 写入 frontmatter）
    import re
    body = text.split("---", 2)[-1] if text.startswith("---") else text
    # 不重新解析图，仅做演示
    print(f"item_id={args.item_id}")
    print(f"cover_url={cover_url}")
    print(f"（请配合 fetch_rss.py 把 images 写入 frontmatter）")

if __name__ == "__main__":
    main()
