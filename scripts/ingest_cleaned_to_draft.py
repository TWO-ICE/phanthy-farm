#!/usr/bin/env python3
"""
ingest_cleaned_to_draft.py
清洗目录 → agent v2 draft 入库

用法:
    python3 ingest_cleaned_to_draft.py <cleaned_dir> <agent_dir> [--dry-run]

例:
    python3 ingest_cleaned_to_draft.py ~/Downloads/年糕亲子生活_清洗 \
        ~/Documents/phanthy/agents/05_ngao-qinzi
"""
import os
import re
import sys
import shutil
from pathlib import Path


def safe_title(title: str) -> str:
    """与 pipeline.py 一致的清洗后标题（去掉文件系统非法字符）"""
    return re.sub(r'[\\/:*?"<>|]', '_', title).strip() or 'untitled'


def main():
    if len(sys.argv) < 3:
        print("用法: ingest_cleaned_to_draft.py <cleaned_dir> <agent_dir> [--dry-run]")
        sys.exit(1)

    cleaned_dir = Path(sys.argv[1]).expanduser()
    agent_dir = Path(sys.argv[2]).expanduser()
    dry_run = '--dry-run' in sys.argv

    if not cleaned_dir.is_dir():
        print(f"[ERR] 清洗目录不存在: {cleaned_dir}")
        sys.exit(1)

    draft_dir = agent_dir / 'draft'
    draft_dir.mkdir(parents=True, exist_ok=True)

    # 取已有最大序号续编
    existing = list(draft_dir.glob('post_*_*.md'))
    max_idx = 0
    for f in existing:
        m = re.match(r'post_(\d{4})_', f.name)
        if m:
            max_idx = max(max_idx, int(m.group(1)))

    md_files = sorted([f for f in cleaned_dir.glob('*.md') if f.is_file()])
    print(f"[INFO] 清洗目录: {cleaned_dir}")
    print(f"[INFO] agent 目录: {agent_dir}")
    print(f"[INFO] draft 已有 {len(existing)} 篇，从 post_{max_idx+1:04d} 开始")
    print(f"[INFO] 待入库: {len(md_files)} 篇 (dry_run={dry_run})")
    print()

    ok, skip, fail = 0, 0, 0
    for src in md_files:
        # 文件名去掉 .md 后缀就是原标题
        title = src.stem
        # 跳过空文件
        if src.stat().st_size < 100:
            skip += 1
            continue

        max_idx += 1
        new_name = f"post_{max_idx:04d}_{safe_title(title)}.md"
        dst = draft_dir / new_name

        if dst.exists():
            print(f"[SKIP] 已存在: {new_name}")
            skip += 1
            max_idx -= 1
            continue

        if dry_run:
            print(f"[DRY] {src.name} -> {new_name}")
        else:
            try:
                shutil.copy2(src, dst)
                ok += 1
            except Exception as e:
                print(f"[FAIL] {src.name}: {e}")
                fail += 1
                max_idx -= 1

    print()
    print(f"完成: 成功{ok} 跳过{skip} 失败{fail}")
    print(f"draft 现存: {len(list(draft_dir.glob('post_*_*.md')))} 篇")


if __name__ == '__main__':
    main()
