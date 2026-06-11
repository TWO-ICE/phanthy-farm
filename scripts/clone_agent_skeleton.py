#!/usr/bin/env python3
"""
clone_agent_skeleton.py
基于一个模板 agent（比如 03_keji-xiansheng）批量克隆骨架到新 agent。

用法:
    python3 clone_agent_skeleton.py <template_dir> <new_agent_dir> <new_name_cn> <new_slug> <new_description>

会修改 AGENT_RULES.md / SOUL.md / PROFILE.md / TUNING.md / AGENT_PROMPT.md 中的 agent 名。
"""
import os
import sys
import shutil
from pathlib import Path


def patch_in_files(root: Path, old_slug: str, old_name_cn: str, new_slug: str, new_name_cn: str, new_desc: str):
    """把模板 agent 提到的旧名字替换为新名字。"""
    # 文本替换映射（按出现顺序）
    for f in root.rglob('*.md'):
        txt = f.read_text(encoding='utf-8')
        new = txt
        # 描述行
        new = new.replace(
            '拆解科技行业的真相。手机、AI、互联网——数据说话，逻辑拆局。',
            new_desc,
        )
        # "keji-xiansheng（科技先生）" 模式
        new = new.replace(f'{old_slug}（{old_name_cn}）', f'{new_slug}（{new_name_cn}）')
        # 单独的 slug
        new = new.replace(old_slug, new_slug)
        # 中文名替换（任何位置，包括 "PROFILE.md — 科技先生" 这种）
        new = new.replace(old_name_cn, new_name_cn)

        if new != txt:
            f.write_text(new, encoding='utf-8')


def main():
    if len(sys.argv) != 6:
        print('用法: clone_agent_skeleton.py <template_dir> <new_agent_dir> <new_name_cn> <new_slug> <new_description>')
        sys.exit(1)

    template = Path(sys.argv[1]).expanduser()
    new_dir = Path(sys.argv[2]).expanduser()
    new_name = sys.argv[3]
    new_slug = sys.argv[4]
    new_desc = sys.argv[5]

    if not template.is_dir():
        print(f'[ERR] 模板不存在: {template}')
        sys.exit(1)

    new_dir.mkdir(parents=True, exist_ok=True)

    # 提取模板的 slug/name（从 AGENT_RULES.md 头部找）
    rules = (template / 'AGENT_RULES.md').read_text(encoding='utf-8')
    import re
    m = re.search(r'#\s*Agent 规则：(\S+)（(.+?)）', rules)
    if not m:
        print(f'[ERR] 模板 AGENT_RULES.md 头部不符合预期: {rules[:80]}')
        sys.exit(1)
    old_slug, old_name = m.group(1), m.group(2)

    print(f'[INFO] 模板: {template.name} ({old_slug} / {old_name})')
    print(f'[INFO] 目标: {new_dir.name} ({new_slug} / {new_name})')

    # 拷贝整个目录（排除 draft/post/archived）
    for item in template.iterdir():
        if item.name in ('draft', 'post', 'archived', 'pending_posts', 'sources', '.DS_Store'):
            continue
        dst = new_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dst)

    # 文本替换
    patch_in_files(new_dir, old_slug, old_name, new_slug, new_name, new_desc)

    # 建空 draft/post
    (new_dir / 'draft').mkdir(exist_ok=True)
    (new_dir / 'post').mkdir(exist_ok=True)

    print(f'[OK] 骨架生成: {new_dir}')


if __name__ == '__main__':
    main()
