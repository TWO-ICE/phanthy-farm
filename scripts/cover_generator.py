#!/usr/bin/env python3
"""
盐选小说封面生成器 v1.0

规范来源：封面设计规范（已确认）- 2026-06-05

布局：
  - 顶部 Y=250：字数统计（40号字）
  - 中央 Y=360 起：标题（100号字，自动换行，8 方向描边）
  - 摘要 Y=600 起：前 200 汉字，智能断行（按 。！？\n 切），最多 8 行
  - 底部 H-80：引导语

摘要提取规则：
  - 跳过标题行（# 开头）
  - 跳过原文链接（> 原文链接）
  - 跳过章节标题（（1）（2）等）
  - 跳过空行
  - 取前 200 汉字，末尾加 "…"
  - 智能断行：优先按 。！？\n 切，超过 25 字硬切
"""

import os
import re
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO = Path(os.environ.get("PHANTHY_REPO", "/Users/4paradigm/Documents/phanthy"))

# ─── 布局常量 ───────────────────────────────────────────
W, H = 896, 1200  # 3:4 比例

TOP_Y = 130            # 顶部字数 Y
TITLE_Y = 340          # 标题起始 Y（下调 70px，加大顶部-标题间距）
EXCERPT_Y = 460        # 摘要起始 Y（标题-摘要间距加大）
EXCERPT_LINE_HEIGHT = 36
EXCERPT_MAX_LINES = 15
EXCERPT_MAX_CHARS = 200  # 前 200 汉字
EXCERPT_LINE_CHARS = 25  # 每行最多 25 字
PARAGRAPH_GAP = 24       # 段间空行（从 50 减小到 24，约 0.7 倍行高）

TITLE_FONT_SIZE = 100
TOP_FONT_SIZE = 32     # 缩小到 32，弱化视觉
EXCERPT_FONT_SIZE = 26  # 26 号，多塞行
BOTTOM_FONT_SIZE = 28

# 颜色
TOP_COLOR = "#999999"  # 浅灰，弱化顶部字数
TITLE_COLOR = "#2d2d2d"
TITLE_STROKE_COLOR = "#8b7355"
EXCERPT_COLOR = "#555555"
BOTTOM_COLOR = "#888888"

# 阅读速度
READ_WPM = 400  # 字/分钟

# 字体 fallback 链
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux 文泉驿
    "/System/Library/Fonts/PingFang.ttc",             # macOS 苹方
    "/System/Library/Fonts/STHeiti Medium.ttc",       # macOS 华文黑体
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",     # macOS 冬青黑
    "/Library/Fonts/Songti.ttc",                      # macOS 宋体
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "C:/Windows/Fonts/msyh.ttc",                      # Windows 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",                    # Windows 黑体
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

def find_font():
    """按 fallback 链找一个可用字体"""
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    # 最后兜底：Pillow 默认
    return None


def extract_title_and_text(content):
    """从 content.md 提取标题和正文"""
    lines = content.split('\n')
    title = None
    text_lines = []
    for line in lines:
        stripped = line.strip()
        if title is None and stripped.startswith('# '):
            title = stripped[2:].strip()
            continue
        if title is not None:
            text_lines.append(line)
    return title or "无标题", '\n'.join(text_lines)


def clean_and_extract_excerpt(content, max_chars=200):
    """清洗 + 提取前 N 汉字 + 按"。"分自然段 + 段间空行"""
    title, body = extract_title_and_text(content)

    # 清洗：跳过空行/章节标题/原文链接/普通标题
    cleaned_lines = []
    for line in body.split('\n'):
        s = line.strip()
        if not s:
            continue
        if s.startswith('> '):
            continue
        if s.startswith('# '):
            continue
        if re.match(r'^（\d+）', s):
            continue
        if s.startswith('💡'):
            continue
        cleaned_lines.append(s)

    full_text = ''.join(cleaned_lines)

    # 字数统计：只算汉字（用全文）
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', full_text)
    # （注：此处不返回值，由调用方另算）

    # 摘要提取：保留汉字+中文标点+数字+英文，取前 200 字符
    EXCERPT_CHARS_RE = r'[一-鿿，。！？；：（）【】《》、…—\-\s0-9A-Za-z]'
    excerpt_chars = re.findall(EXCERPT_CHARS_RE, full_text)
    truncated = len(excerpt_chars) > max_chars
    excerpt = ''.join(excerpt_chars[:max_chars])
    if truncated:
        excerpt += '…'

    # 按"。"分句（保留句末标点）
    parts = re.split(r'([。！？\n])', excerpt)
    sentences = []
    for i in range(0, len(parts) - 1, 2):
        s = parts[i] + parts[i+1]
        if s.strip():
            sentences.append(s)
    if len(parts) % 2 == 1 and parts[-1].strip():
        sentences.append(parts[-1])

    # 每 2 句合并为一个"自然段"
    paragraphs = []
    for i in range(0, len(sentences), 2):
        p = ''.join(sentences[i:i+2])
        paragraphs.append(p)

    # 每段内按 25 字软切（优先在"。"和"，"等标点处切）
    SOFT_CUT_CHARS = "。！？；：、，"
    lines = []
    for p in paragraphs:
        if len(p) <= EXCERPT_LINE_CHARS:
            lines.append(p)
        else:
            remaining = p
            while len(remaining) > EXCERPT_LINE_CHARS:
                # 找最近的标点（≤25字 内）
                cut = -1
                for i in range(EXCERPT_LINE_CHARS, 0, -1):
                    if i < len(remaining) and remaining[i] in SOFT_CUT_CHARS:
                        cut = i + 1  # 切在标点后
                        break
                if cut == -1:
                    cut = EXCERPT_LINE_CHARS  # 无标点，硬切
                lines.append(remaining[:cut])
                remaining = remaining[cut:]
            if remaining:
                lines.append(remaining)
        lines.append("")  # 段末空行标记

    # 去掉末尾空行
    while lines and lines[-1] == "":
        lines.pop()

    return title, lines


def wrap_title(title, max_chars=7):
    """标题自动换行（按字符数切，避免拆词组）

    关键规则：
    1. 中文标点算 1 字符
    2. 中文虚词（之/的/了/...）若出现在行末，下一个字应同行
    3. 中文介词（上/中/下/里/...）若出现在词中，把前一个实词踢出来绑定
    4. 短标题不强制换行
    """
    # 中文虚词集合（行末是虚词 → 虚词+下一字绑定）
    BOUND_CHARS = set("之的了和与或但而却也还都已着过及其")
    # 中文介词/方位词集合（当前字是介词 → 前一个实词+当前介词绑定）
    PREP_CHARS = set("上中下里外内前后左右")
    PUNCTUATION = "？！。，、；：…—-"

    # 短标题直接 1 行
    if len(title) <= max_chars:
        return [title]

    lines = []
    current = ""
    chars = list(title)
    for c in chars:
        # 规则 1：当前字是介词 → 把前一个实词踢出来绑定
        if (c in PREP_CHARS and current 
            and current[-1] not in BOUND_CHARS 
            and current[-1] not in PREP_CHARS
            and c not in PUNCTUATION):
            bound_word = current[-1]
            current = current[:-1]
            current += bound_word + c
            continue
        # 规则 2：current 满员
        if len(current) >= max_chars:
            # 2a: current 末尾是虚词 + 当前字是实词（非标点）→ 虚词+实词绑定
            if (current[-1] in BOUND_CHARS 
                and c not in BOUND_CHARS 
                and c not in PUNCTUATION):
                bound = current[-1]
                current = current[:-1]
                current += bound + c
                continue
            # 2b: 否则正常 wrap
            lines.append(current)
            current = c
        else:
            current += c
    if current:
        # 短标点附加到上一行
        if lines and len(current) <= 2 and all(ch in PUNCTUATION for ch in current):
            lines[-1] += current
        else:
            lines.append(current)
    return lines


def draw_text_with_stroke(draw, xy, text, font, fill, stroke_fill, stroke_width=2):
    """8 方向描边 + 主体文字"""
    x, y = xy
    offsets = [
        (0, -stroke_width), (0, stroke_width),
        (-stroke_width, 0), (stroke_width, 0),
        (stroke_width, stroke_width), (-stroke_width, -stroke_width),
        (stroke_width, -stroke_width), (-stroke_width, stroke_width),
    ]
    for dx, dy in offsets:
        draw.text((x + dx, y + dy), text, font=font, fill=stroke_fill, anchor='mm')
    draw.text((x, y), text, font=font, fill=fill, anchor='mm')


def generate_cover(post_dir, agent_path, output_path=None):
    """生成单篇封面"""
    content_file = os.path.join(post_dir, 'content.md')
    if not os.path.exists(content_file):
        print(f"  ⚠️ content.md 不存在: {post_dir}")
        return False

    content = open(content_file).read()
    title, excerpt_lines = clean_and_extract_excerpt(content, EXCERPT_MAX_CHARS)

    # 字数
    char_count = len(re.findall(r'[\u4e00-\u9fff]', content))
    read_time = max(1, char_count // READ_WPM)

    # 背景图
    bg_path = os.path.join(agent_path, '款式3_3x4.png')
    if os.path.exists(bg_path):
        img = Image.open(bg_path).convert('RGB')
        if img.size != (W, H):
            img = img.resize((W, H), Image.LANCZOS)
    else:
        # 兜底：浅灰渐变
        img = Image.new('RGB', (W, H), '#f5f3ed')

    draw = ImageDraw.Draw(img)

    # 字体
    font_path = find_font()
    if font_path:
        top_font = ImageFont.truetype(font_path, TOP_FONT_SIZE)
        title_font = ImageFont.truetype(font_path, TITLE_FONT_SIZE)
        excerpt_font = ImageFont.truetype(font_path, EXCERPT_FONT_SIZE)
        bottom_font = ImageFont.truetype(font_path, BOTTOM_FONT_SIZE)
    else:
        top_font = title_font = excerpt_font = bottom_font = ImageFont.load_default()

    # 顶部字数
    top_text = f"全文{char_count}字 · 阅读需{read_time}分钟"
    draw.text((W // 2, TOP_Y), top_text, font=top_font, fill=TOP_COLOR, anchor='mm')

    # 标题（自动换行 + 8 方向描边 + 自适应字号）
    # 循环降字号直到 ≤ 2 行，按字号反算 max_chars 保证左右各 80px 边距
    SIDE_MARGIN = 80
    target_width = W - 2 * SIDE_MARGIN  # 736
    title_font_size = TITLE_FONT_SIZE
    max_chars = 7
    title_lines = wrap_title(title, max_chars=max_chars)
    for size in [100, 80, 72, 64, 56, 50, 44, 40, 36, 32, 28, 24]:
        font_test = ImageFont.truetype(font_path, size) if font_path else None
        if font_test:
            # 实测"中"字宽，反算 max_chars
            char_w = font_test.getbbox("中")[2] - font_test.getbbox("中")[0]
            mc = max(1, int(target_width / char_w))
        else:
            mc = 7
        lines = wrap_title(title, max_chars=mc)
        if len(lines) <= 2:
            title_font_size = size
            max_chars = mc
            title_lines = lines
            break
        # 否则继续降字号

    title_font = ImageFont.truetype(font_path, title_font_size) if font_path else title_font

    # 多行标题垂直居中（以 TITLE_Y 为中心）
    line_height = int(title_font_size * 1.1)
    total_height = (len(title_lines) - 1) * line_height
    title_y_start = TITLE_Y - total_height // 2
    for i, line in enumerate(title_lines):
        y = title_y_start + i * line_height
        draw_text_with_stroke(
            draw, (W // 2, y), line, title_font,
            fill=TITLE_COLOR, stroke_fill=TITLE_STROKE_COLOR, stroke_width=3
        )
    title_bottom = title_y_start + (len(title_lines) - 1) * line_height  # 标题最后一行 Y

    # 动态确定摘要起始 Y：标题后留 100px 缓冲
    excerpt_y = max(EXCERPT_Y, title_bottom + 100)
    # 摘要实际行数（最多 15 行，但底部还要留 180px 给装饰+副标题+底部）
    available_height = H - 180 - excerpt_y  # 180 = 装饰线+副标题+底部
    max_lines_by_space = max(3, int(available_height // EXCERPT_LINE_HEIGHT))
    actual_max_lines = min(EXCERPT_MAX_LINES, max_lines_by_space, len(excerpt_lines))

    # 摘要（按段绘制，空行作段间距）
    y = excerpt_y
    for line in excerpt_lines[:EXCERPT_MAX_LINES]:
        if not line.strip():
            y += PARAGRAPH_GAP  # 段间空行
            continue
        draw.text((W // 2, y), line, font=excerpt_font, fill=EXCERPT_COLOR, anchor='mm')
        y += EXCERPT_LINE_HEIGHT

    # 装饰分隔线（紧贴摘要结束 + 30px）
    sep_y = y + 30
    sep_y = min(sep_y, H - 140)
    line_w = 60
    draw.line([(W//2 - line_w, sep_y), (W//2 - 12, sep_y)], fill="#8b7355", width=1)
    draw.line([(W//2 + 12, sep_y), (W//2 + line_w, sep_y)], fill="#8b7355", width=1)
    draw.polygon([(W//2, sep_y-4), (W//2+4, sep_y), (W//2, sep_y+4), (W//2-4, sep_y)], fill="#8b7355")

    # CTA 按钮：圆角矩形 + "点击阅读全文"
    cta_y = H - 50
    cta_text = "点击阅读全文"
    cta_font_size = 36
    cta_font = ImageFont.truetype(font_path, cta_font_size) if font_path else bottom_font
    # 计算按钮宽度
    bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
    cta_w = bbox[2] - bbox[0] + 80
    cta_h = 68
    cta_x1 = W//2 - cta_w//2
    cta_x2 = W//2 + cta_w//2
    cta_y1 = cta_y - cta_h//2
    cta_y2 = cta_y + cta_h//2
    # 画圆角按钮
    draw.rounded_rectangle([(cta_x1, cta_y1), (cta_x2, cta_y2)],
                           radius=cta_h//2, fill="#8b7355")
    draw.text((W//2, cta_y), cta_text, font=cta_font, fill="#ffffff", anchor='mm')

    # 保存
    if output_path is None:
        output_path = os.path.join(post_dir, 'cover.png')
    img.save(output_path, 'PNG', quality=95)

    print(f"  ✅ 封面生成: {output_path}")
    print(f"     标题: {title} ({len(title_lines)}行)")
    print(f"     字数: {char_count} 字 / 阅读需 {read_time} 分钟")
    print(f"     摘要: {len(excerpt_lines)} 行")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="盐选小说封面生成")
    parser.add_argument("--agent", required=True, help="Agent slug")
    parser.add_argument("--folder", help="指定单个文件夹名")
    parser.add_argument("--count", type=int, help="生成最近 N 篇")
    parser.add_argument("--all", action="store_true", help="生成所有 post/")
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
            folders = folders[-args.count:]  # 最近的 N 篇

    print(f"🎨 封面生成 - {args.agent}")
    print(f"   待处理: {len(folders)} 篇\n")

    success = 0
    for f in folders:
        if generate_cover(os.path.join(post_dir, f), agent_path):
            success += 1

    print(f"\n🏁 完成！成功 {success}，失败 {len(folders) - success}")


if __name__ == "__main__":
    main()
