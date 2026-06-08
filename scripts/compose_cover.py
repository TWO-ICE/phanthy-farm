#!/usr/bin/env python3
"""
封面图层合成：底图 + 标题字 = 最终封面。

用法:
  python3 compose_cover.py \
    --bg path/to/bg.png \
    --title "OPPO Bubble..." \
    --out path/to/01_cover.png \
    --tools-md ~/phanthy-farm/agents/linajie/TOOLS.md
"""
import argparse, json, os, sys, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DEFAULT_STYLE = {
    "font_path": "/System/Library/Fonts/PingFang.ttc",
    "font_size": 64,
    "font_color": "#1A1A1A",
    "title_position": "top_20pct",
    "stroke": {"color": "#FFFFFF", "width": 2},
}

def load_style(tools_md: Path | None) -> dict:
    if not tools_md or not tools_md.exists():
        return DEFAULT_STYLE
    # 简易解析（实际可改成 yaml）
    txt = tools_md.read_text()
    style = dict(DEFAULT_STYLE)
    # 找 cover_style: ... 区块
    if "cover_style:" in txt:
        block = txt.split("cover_style:", 1)[1].split("\n\n", 1)[0]
        for line in block.split("\n"):
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                k, v = [p.strip() for p in line.split(":", 1)]
                v = v.strip('"').strip("'")
                if k in style:
                    style[k] = v
    return style

def hex2rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def compose(bg: Path, title: str, out: Path, style: dict):
    img = Image.open(bg).convert("RGB")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(style["font_path"], int(style["font_size"]))

    # 自动换行
    max_w = int(img.width * 0.85)
    lines = []
    for line in textwrap.wrap(title, width=20):
        bbox = draw.textbbox((0, 0), line, font=font)
        if bbox[2] > max_w:
            # 进一步拆
            for sub in textwrap.wrap(line, width=14):
                lines.append(sub)
        else:
            lines.append(line)

    # 计算总高度 + 起始 Y
    line_h = int(style["font_size"]) * 1.3
    total_h = line_h * len(lines)
    pos = style["title_position"]
    if pos == "top_20pct":
        y0 = int(img.height * 0.20)
    elif pos == "center":
        y0 = int((img.height - total_h) / 2)
    elif pos == "bottom_20pct":
        y0 = int(img.height * 0.80 - total_h)
    else:
        y0 = int(img.height * 0.20)

    stroke = style.get("stroke") or {}
    stroke_w = int(stroke.get("width", 0))
    stroke_rgb = hex2rgb(stroke.get("color", "#FFFFFF")) if stroke else None
    color_rgb = hex2rgb(style["font_color"])

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = int((img.width - w) / 2)
        y = int(y0 + i * line_h)
        if stroke_w and stroke_rgb:
            draw.text((x, y), line, font=font, fill=color_rgb,
                      stroke_width=stroke_w, stroke_fill=stroke_rgb)
        else:
            draw.text((x, y), line, font=font, fill=color_rgb)

    img.save(out, quality=92)
    print(f"✅ composed → {out}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tools-md", default=None)
    args = ap.parse_args()

    style = load_style(Path(args.tools_md).expanduser() if args.tools_md else None)
    compose(Path(args.bg), args.title, Path(args.out), style)

if __name__ == "__main__":
    main()
