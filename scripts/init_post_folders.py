#!/usr/bin/env python3
"""
init_post_folders.py — 把清洗后的 md 灌到 pending_posts/ 当作仿写素材

【v3 规范】新工作流第一阶段：
  - 输入：~/Downloads/{mp}_清洗/*.md （清洗后的公众号原文）
  - 输出：agents/{slug}/pending_posts/post_XX_<short_title>/source.md
          （只拷 source.md；content.md 留给 complete 阶段 LLM 深度仿写产出）
  - 编号：接续现有最大 post_XX
  - 标题：去特殊字符、限 max_title_length 字符
  - 去重：同标题跳过
  - 状态：init 后都是 "未完"，等 complete 阶段仿写 + 补素材

用法:
  python3 init_post_folders.py --agent-slug xiaoyu-tech --clean-dir ~/Downloads/小鱼科技v_清洗
  python3 init_post_folders.py --agent-slug xiaoyu-tech --clean-dir ~/Downloads/小鱼科技v_清洗 --dry-run
  python3 init_post_folders.py --agent-slug xiaoyu-tech --clean-dir ~/Downloads/小鱼科技v_清洗 --max-title-length 30
"""
import argparse, json, os, re, sys
from pathlib import Path

# 真实仓库路径
FARM_ROOT_CANDIDATES = [
    Path(os.environ.get("PHANTHY_REPO", "/Users/4paradigm/Documents/phanthy")),
    Path(os.path.expanduser("~/phanthy-farm")),
]
FARM_ROOT = next((p for p in FARM_ROOT_CANDIDATES if p.exists()), FARM_ROOT_CANDIDATES[0])


def safe_title(title: str, max_len: int = 30) -> str:
    """
    清理标题用作目录名：
    - 去特殊字符：\\/:*?"<>|
    - 限 max_len 字符
    - 去多余空格
    - 去掉末尾的"完"字（防 audit 误判为已完成状态）

    关键：必须先截 max_len 再去末尾"完"，否则截断位置恰好停在"完"字中间时
    会留下 "...跑飞牛完"（"完"在中间，不是末尾，rstrip 去不掉）。
    """
    title = title.strip()
    # 去特殊字符
    title = re.sub(r'[\\/:*?"<>|]', '_', title)
    # 去连续下划线
    title = re.sub(r'_+', '_', title)
    # 去首尾空格和下划线
    title = title.strip('_').strip()
    # 先限长（重要！）
    if len(title) > max_len:
        title = title[:max_len]
    # 再去末尾"完"字（极少见但要防，否则 audit 会误判为 done）
    title = re.sub(r'完+$', '', title)
    return title.rstrip('_').strip()


def get_next_post_index(pending_dir: Path) -> int:
    """扫描现有 post_XX_xxx/ 找最大 XX + 1"""
    max_idx = 0
    for d in pending_dir.iterdir():
        if not d.is_dir():
            continue
        m = re.match(r'^post_(\d+)_', d.name)
        if m:
            n = int(m.group(1))
            if n > max_idx:
                max_idx = n
    return max_idx + 1


def parse_clean_md(md_path: Path):
    """从清洗 md 提取：title, body_chars"""
    text = md_path.read_text(encoding='utf-8')
    title = ""
    for line in text.split('\n'):
        if line.startswith('# '):
            title = line[2:].strip()
            break
    # 字数：去标题/封面图/原文链接后的正文
    body_text = text
    for pat in [r'^# .+\n', r'!\[封面图\]\([^)]+\)\n', r'> 原文链接：.+\n']:
        body_text = re.sub(pat, '', body_text, flags=re.M)
    plain = body_text
    for ch in "#*>\n\t -|":
        plain = plain.replace(ch, "")
    return title, len(plain)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--agent-slug', required=True)
    ap.add_argument('--clean-dir', required=True, help='清洗md目录')
    ap.add_argument('--max-title-length', type=int, default=30, help='短标题最大字符数（默认30）')
    ap.add_argument('--min-chars', type=int, default=200, help='最低字数（过滤空md）')
    ap.add_argument('--dry-run', action='store_true', help='只看会建哪些，不真建')
    args = ap.parse_args()

    REPO = FARM_ROOT
    PENDING = REPO / 'agents' / args.agent_slug / 'pending_posts'
    CLEAN_DIR = Path(args.clean_dir).expanduser()

    if not PENDING.exists():
        print(f'❌ pending_posts 不存在: {PENDING}', file=sys.stderr)
        sys.exit(1)
    if not CLEAN_DIR.exists():
        print(f'❌ 清洗目录不存在: {CLEAN_DIR}', file=sys.stderr)
        sys.exit(1)

    # 1. 找最大 post 编号
    next_idx = get_next_post_index(PENDING)
    # 数字序排序展示（按 post_XX 中的 XX 排，不是字典序）
    def numeric_key(name):
        m = re.match(r'^post_(\d+)_', name)
        return int(m.group(1)) if m else 0
    print(f'=== init_post_folders.py ===')
    print(f'  agent:   {args.agent_slug}')
    print(f'  clean:   {CLEAN_DIR}')
    print(f'  pending: {PENDING}')
    print(f'  next_idx={next_idx} (现有最大 + 1)')
    print(f'  max_title_length={args.max_title_length}, min_chars={args.min_chars}')
    if args.dry_run:
        print(f'  *** DRY-RUN 模式：不实际创建 ***')

    # 2. 扫清洗md，按字数排序
    candidates = []
    for md_path in CLEAN_DIR.glob('*.md'):
        title, body_chars = parse_clean_md(md_path)
        candidates.append({
            'md_path': md_path,
            'title': title,
            'body_chars': body_chars,
        })
    candidates.sort(key=lambda x: x['body_chars'], reverse=True)
    print(f'\n[1/3] 清洗md总数: {len(candidates)}')

    # 3. 收集现有短标题（避免重复建）
    existing_short_titles = set()
    for d in PENDING.iterdir():
        if d.is_dir():
            # post_01_xxx → xxx
            parts = d.name.split('_', 2)
            if len(parts) >= 3:
                existing_short_titles.add(parts[2].rstrip('完'))
    print(f'     pending_posts 现有目录: {sum(1 for d in PENDING.iterdir() if d.is_dir())}')
    print(f'     现有短标题（去"完"）: {len(existing_short_titles)}')

    # 4. 逐个创建
    print(f'\n[2/3] 开始创建 (从 post_{next_idx:02d} 开始)...')
    created = 0
    skip_empty = 0
    skip_duplicate = 0
    skip_existing_idx = 0

    new_dirs = []  # 记录新建的，供 dry-run 展示
    fill_existing = []  # 已存在但 content.md 缺失的，需要补全

    for c in candidates:
        title = c['title']
        chars = c['body_chars']

        if chars < args.min_chars:
            skip_empty += 1
            continue

        short = safe_title(title, args.max_title_length)
        if not short:
            skip_empty += 1
            continue

        if short in existing_short_titles:
            skip_duplicate += 1
            # 查该 short 对应的 post_XX_<short> 目录是否真的存在（仅 matched 的才算"已建过"）
            # 用实际目录名匹配，不靠 short 反推
            continue

        idx = next_idx
        next_idx += 1

        post_dir_name = f'post_{idx:02d}_{short}'
        post_dir = PENDING / post_dir_name

        # 防重名
        if post_dir.exists():
            skip_existing_idx += 1
            continue

        new_dirs.append({
            'idx': idx,
            'dir_name': post_dir_name,
            'title': title,
            'short': short,
            'chars': chars,
        })
        existing_short_titles.add(short)
        created += 1

    # 扫一遍：找出"短标题已存在但目录无 content.md"的目录（断点序跳过 + 之前被删空的情况）
    # 注意：目录 short 跟 candidates 里的 safe_title 输出可能有末尾空格差异（老版本未 strip），
    # 比较时双 strip 一致性
    for d in PENDING.iterdir():
        if not d.is_dir():
            continue
        if not (d / 'content.md').exists():
            m = re.match(r'^post_\d+_(.+?)$', d.name)
            if not m:
                continue
            short = m.group(1).strip()
            for c in candidates:
                st = safe_title(c['title'], args.max_title_length).strip()
                if st == short and c['body_chars'] >= args.min_chars:
                    fill_existing.append({
                        'dir_name': d.name,
                        'title': c['title'],
                        'short': st,
                        'chars': c['body_chars'],
                    })
                    break

    # dry-run 只展示
    if args.dry_run:
        print(f'\n  计划创建 {len(new_dirs)} 个:')
        for d in new_dirs[:30]:
            print(f'    {d["dir_name"]} | chars={d["chars"]} | {d["title"][:40]}')
        if len(new_dirs) > 30:
            print(f'    ... 还有 {len(new_dirs)-30} 个')
        print(f'\n  跳过 短文={skip_empty}, 重复短标题={skip_duplicate}, 重名idx={skip_existing_idx}')
        return

    # 真创建 + 补全已有空目录
    print(f'\n[3/3] 创建 {len(new_dirs)} 个 + 补全 {len(fill_existing)} 个空目录...')
    title_to_md = {c['title']: c['md_path'] for c in candidates}

    for d in new_dirs:
        post_dir = PENDING / d['dir_name']
        post_dir.mkdir(parents=True, exist_ok=True)
        dst_md = post_dir / 'source.md'  # 仿写素材（原文）
        if not dst_md.exists():
            src_md = title_to_md.get(d['title'])
            if src_md:
                dst_md.write_text(src_md.read_text(encoding='utf-8'), encoding='utf-8')
        # content.md 不在这里创建，留给 complete_post_folders.py 调 LLM 仿写产出
        if created <= 5 or created % 100 == 0:
            print(f'    ✅ {d["dir_name"]} | chars={d["chars"]} | {d["title"][:40]}')

    # 补全已存在的空目录（断点续传跳过但实际为空的情况）
    fill_ok = 0
    for d in fill_existing:
        post_dir = PENDING / d['dir_name']
        dst_md = post_dir / 'source.md'
        if dst_md.exists():
            continue
        src_md = title_to_md.get(d['title'])
        if src_md:
            dst_md.write_text(src_md.read_text(encoding='utf-8'), encoding='utf-8')
            fill_ok += 1
    if fill_existing:
        print(f'    补全 {fill_ok} 个空目录')

    print(f'\n[Done] 新建 {created}, 补全 {fill_ok}, 跳过 短文={skip_empty}, 重复={skip_duplicate}, 重名={skip_existing_idx}')
    print(f'输出: {PENDING}')
    print(f'\n[Next] 跑 complete_post_folders.py 仿写 + 补素材（content.md / reference.jpg / img_*.jpg / manifest / cover prompt）')


if __name__ == '__main__':
    main()
