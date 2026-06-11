#!/usr/bin/env python3
"""
push_agent_to_gitee.py
把单个 agent 推送到 Gitee 独立仓库，过滤 draft/ 和 archived/。

用法:
    python3 push_agent_to_gitee.py <agent_slug>

例:
    python3 push_agent_to_gitee.py hufu-mo-di
"""
import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

GITEE_TOKEN = 'f125d7e6a305a4986879a3b64ee84e48'
GITEE_USER = 'twoice'
GITEE_API = 'https://gitee.com/api/v5'

AGENTS_ROOT = Path('/Users/4paradigm/Documents/phanthy/agents')
REPOS_ROOT = Path('/Users/4paradigm/Documents/phanthy/repos')

# 过滤规则：这些目录/文件绝不入仓
EXCLUDE_DIRS = {'draft', 'archived', 'pending_posts', '.DS_Store', 'repos', 'sources'}

# Gitee 仓里只放 post/，其它一律过滤
INCLUDED_PATHS = {'post'}


def gitee_create_repo(slug: str) -> bool:
    """在 Gitee 上创建公开仓库（已存在则忽略）。"""
    import requests
    repo_name = f'phanthy-{slug}'
    url = f'{GITEE_API}/user/repos'
    r = requests.post(
        url,
        params={'access_token': GITEE_TOKEN},
        json={
            'name': repo_name,
            'description': f'Phanthy agent: {slug}',
            'private': False,
            'auto_init': True,
        },
        timeout=30,
    )
    if r.status_code == 201:
        print(f'[GITEE] 创建仓库: {repo_name}')
        return True
    elif r.status_code == 422 and ('exists' in r.text.lower() or '已存在' in r.text):
        print(f'[GITEE] 仓库已存在: {repo_name}')
        return True
    else:
        print(f'[ERR] 创建仓库失败: {r.status_code} {r.text[:200]}')
        return False


def build_filtered_copy(agent_dir: Path, workdir: Path):
    """Gitee 仓里只放 post/，其它全部过滤。"""
    for item in agent_dir.iterdir():
        if item.name not in INCLUDED_PATHS:
            continue
        if item.name.startswith('.'):
            continue
        dst = workdir / item.name
        if item.is_dir():
            shutil.copytree(item, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dst)


def main():
    if len(sys.argv) != 2:
        print('用法: push_agent_to_gitee.py <agent_slug>')
        sys.exit(1)

    slug = sys.argv[1]
    agent_dir = AGENTS_ROOT / f'{slug[:2]}_{slug.split("-", 1)[0] if False else slug}'
    # 找到形如 04_hufu-mo-di 的实际目录
    matches = list(AGENTS_ROOT.glob(f'*_{slug}'))
    if not matches:
        print(f'[ERR] 找不到 agent 目录: *_{slug}')
        sys.exit(1)
    agent_dir = matches[0]
    print(f'[INFO] agent 目录: {agent_dir}')

    if not gitee_create_repo(slug):
        sys.exit(1)

    # 准备临时目录做 commit
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp) / 'repo'
        workdir.mkdir()

        # git init
        subprocess.run(['git', 'init', '-b', 'main'], cwd=workdir, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'agent@phanthy.local'],
                       cwd=workdir, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'phanthy-bot'],
                       cwd=workdir, check=True, capture_output=True)

        # 拷贝过滤后的内容
        build_filtered_copy(agent_dir, workdir)

        # commit
        subprocess.run(['git', 'add', '-A'], cwd=workdir, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'agent: {slug}'],
                       cwd=workdir, check=True, capture_output=True)

        # 加 remote
        remote_url = f'https://{GITEE_USER}:{GITEE_TOKEN}@gitee.com/{GITEE_USER}/phanthy-{slug}.git'
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url],
                       cwd=workdir, check=True, capture_output=True)

        # push
        r = subprocess.run(['git', 'push', '-u', 'origin', 'main', '--force'],
                           cwd=workdir, capture_output=True, text=True)
        print(r.stdout)
        if r.returncode != 0:
            print(f'[ERR] push 失败: {r.stderr}')
            sys.exit(1)
        print(f'[OK] {slug} 推送到 Gitee')


if __name__ == '__main__':
    main()
