#!/usr/bin/env python3
"""
正文图片生成器 v1.0

规范来源：正文图片设计规范（已确认）- 2026-06-05

布局：
  - Y=50：标题（40号字，居中，#8b4513）
  - Y=75：分隔线（#cccccc，1px）
  - Y=120 起：正文（24号字，行高 59px，每行 33 字）
  - Y=1180：页码（18号，#888888，居中）

关键修复：按段落切分（不按整字符流硬切），保留段落结构

用法：
  python3 body_image_generator.py --agent onehu-zhihu --folder "post_1498_..."
  python3 body_image_generator.py --agent onehu-zhihu --count 1
"""

import argparse
import math
import os
import re
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO = Path(os.environ.get("PHANTHY_REPO", "/Users/4paradigm/Documents/phanthy"))

# ─── 布局常量（来自 v1 规范） ───────────────────────────
W, H = 896, 1200

FONT_SIZE = 24
LINE_GAP = 35
LINE_HEIGHT = 59       # 24 + 35
MAX_LINES = 17         # 每页行数
CHARS_PER_LINE = 33    # 每行字符

LEFT_MARGIN = 60
RIGHT_MARGIN = 40

TOP_MARGIN_TITLE = 50
TOP_MARGIN_TEXT = 120
BOTTOM_MARGIN = 40

# 颜色
TITLE_COLOR = "#8b4513"   # saddle brown
DIVIDER_COLOR = "#cccccc"
TEXT_COLOR = "#2d2d2d"
PAGE_NUM_COLOR = "#888888"

# 字体 fallback 链（Mac/Linux 兼容）
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Songti.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
]



def resolve_agent_dir(repo, agent_name):
    """自动匹配带序号的agent目录，如 onehu-zhihu → 01_onehu-zhihu"""
    agents_dir = os.path.join(repo, "agents")
    # 精确匹配
    if os.path.isdir(os.path.join(agents_dir, agent_name)):
        return os.path.join(agents_dir, agent_name)
    # 带序号匹配
    for d in os.listdir(agents_dir):
        if d.endswith("_" + agent_name) or d == agent_name:
            return os.path.join(agents_dir, d)
    return os.path.join(agents_dir, agent_name)

def find_font(size):
    """按 fallback 链找一个可用字体"""
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def extract_title_and_body(content_md):
    """从 content.md 提取标题和正文

    content.md 格式（v4）：
      # 标题
      （空行）
      正文...
      （空行）
      > 💡 深度启发自：[标题](URL)
    """
    lines = content_md.split('\n')
    title = None
    body_lines = []
    for line in lines:
        if title is None and line.strip().startswith('# '):
            title = line.strip()[2:].strip()
            continue
        if title is not None:
            body_lines.append(line)
    body = '\n'.join(body_lines).strip()
    return title or "无标题", body


def clean_body(body):
    """清理正文：跳过溯源行、保留段落结构

    返回：paragraphs（list[str]），空段被过滤
    """
    paragraphs = []
    for line in body.split('\n'):
        s = line.strip()
        if not s:
            continue
        if s.startswith('💡'):
            continue
        if s.startswith('> '):
            # 跳过溯源/引用
            continue
        paragraphs.append(s)
    return paragraphs


def split_paragraphs_to_lines(paragraphs, chars_per_line=33):
    """按段落切分：每段内 33 字硬切

    关键修复（v1 规范）：不按整字符流切分，按段落分别切分
    """
    all_lines = []
    for para in paragraphs:
        if not para.strip():
            continue
        for i in range(0, len(para), chars_per_line):
            all_lines.append(para[i:i+chars_per_line])
    return all_lines


def wrap_title(title, max_chars=14):
    """标题截断或换行：每行最多 14 字"""
    if len(title) <= max_chars:
        return [title]
    lines = []
    for i in range(0, len(title), max_chars):
        lines.append(title[i:i+max_chars])
    return lines


def generate_body_images(post_dir, agent_path, output_dir_name="body_pages", max_pages=20):
    """为一篇 post 生成正文图（最多 20 张）"""
    content_file = os.path.join(post_dir, 'content.md')
    if not os.path.exists(content_file):
        print(f"  ⚠️ content.md 不存在: {post_dir}")
        return False

    with open(content_file) as f:
        content = f.read()

    title, body = extract_title_and_body(content)
    paragraphs = clean_body(body)
    all_lines = split_paragraphs_to_lines(paragraphs, CHARS_PER_LINE)
    total_lines = len(all_lines)
    total_pages = max(1, math.ceil(total_lines / MAX_LINES))

    # 限制最多 20 张
    if total_pages > max_pages:
        print(f"  ⚠️ 原文 {total_lines} 行 → 理论 {total_pages} 页，截断到 {max_pages} 张")
        total_pages = max_pages
    else:
        print(f"  标题: {title}")
        print(f"  总行数: {total_lines} → 总页数: {total_pages}")

    # 加载背景
    bg_path = os.path.join(agent_path, '款式3_3x4.png')
    if not os.path.exists(bg_path):
        print(f"  ⚠️ 背景图不存在: {bg_path}")
        return False
    bg = Image.open(bg_path).convert('RGB')
    if bg.size != (W, H):
        bg = bg.resize((W, H), Image.LANCZOS)

    # 字体
    title_font = find_font(40)
    text_font = find_font(FONT_SIZE)
    page_num_font = find_font(18)

    # 输出目录
    out_dir = os.path.join(post_dir, output_dir_name)
    os.makedirs(out_dir, exist_ok=True)

    # 生成每页
    for page_num in range(total_pages):
        start_line = page_num * MAX_LINES
        end_line = min(start_line + MAX_LINES, total_lines)
        page_lines = all_lines[start_line:end_line]

        page_img = bg.copy()
        draw = ImageDraw.Draw(page_img)

        # 标题（自动换行，最多 2 行）—— 动态计算分隔线/正文 Y
        # 用字号 1.2 倍算行高（40号字真实高度 38px，line_height ≥ 48）
        title_lines = wrap_title(title, max_chars=14)
        title_font_size = 40
        title_line_height = int(title_font_size * 1.2)  # 48
        title_padding_after = 15  # 标题底到分隔线
        for i, line in enumerate(title_lines[:2]):
            draw.text((W // 2, TOP_MARGIN_TITLE + i * title_line_height), line,
                      font=title_font, fill=TITLE_COLOR, anchor='mm')
        # 标题区底部 = 最后一行 Y + 一半字号 + padding
        n_title = min(len(title_lines), 2)
        last_title_y = TOP_MARGIN_TITLE + (n_title - 1) * title_line_height
        # anchor='mm' 时文字中心对齐，底部 = center + half_size
        title_block_bottom = last_title_y + title_font_size // 2 + 5
        divider_y = title_block_bottom + title_padding_after
        text_y = divider_y + 25

        # 分隔线
        draw.line([(LEFT_MARGIN, divider_y),
                   (W - RIGHT_MARGIN, divider_y)],
                  fill=DIVIDER_COLOR, width=1)

        # 正文（动态 text_y 起，每行 59px）
        y = text_y
        for line in page_lines:
            draw.text((LEFT_MARGIN, y), line,
                      font=text_font, fill=TEXT_COLOR)
            y += LINE_HEIGHT

        # 页码
        page_text = f"第 {page_num + 1}/{total_pages} 页"
        draw.text((W // 2, H - 20), page_text,
                  font=page_num_font, fill=PAGE_NUM_COLOR, anchor='mm')

        # 保存
        out_path = os.path.join(out_dir, f"page_{page_num + 1:03d}.png")
        page_img.save(out_path, 'PNG', quality=95)

    print(f"  ✅ 生成 {total_pages} 页 → {out_dir}")
    return True


def main():
    parser = argparse.ArgumentParser(description="正文图片生成器")
    parser.add_argument("--agent", required=True, help="Agent slug")
    parser.add_argument("--folder", help="指定单个 post 文件夹")
    parser.add_argument("--count", type=int, help="生成最近 N 篇")
    args = parser.parse_args()

    agent_path = resolve_agent_dir(REPO, args.agent)
    post_dir = os.path.join(agent_path, "post")
    if not os.path.isdir(post_dir):
        print(f"❌ post 目录不存在: {post_dir}")
        sys.exit(1)

    if args.folder:
        folders = [args.folder]
    else:
        folders = sorted(os.listdir(post_dir))
        if args.count:
            folders = folders[-args.count:]

    print(f"📖 正文图片生成 - {args.agent}")
    print(f"   待处理: {len(folders)} 篇\n")

    success = 0
    for f in folders:
        if generate_body_images(os.path.join(post_dir, f), agent_path):
            success += 1

    print(f"\n🏁 完成！成功 {success}，失败 {len(folders) - success}")


if __name__ == "__main__":
    main()
