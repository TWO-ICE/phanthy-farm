#!/usr/bin/env python3
"""知乎盐选素材一条龙补充脚本。
按 TUNING.md 三步流程：仿写 → 封面 → 正文图片，每篇三件套完整再继续。
用法: python3 supply_onehu.py --count 20
"""
import argparse, os, sys, subprocess, shutil

REPO = "/Users/4paradigm/Documents/phanthy"


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

def run(cmd):
    """运行命令，实时输出"""
    print(f"  🔧 $ {cmd}")
    result = subprocess.run(
        cmd, shell=True, cwd=REPO,
        env={**os.environ, "NO_PROXY": "*", "PYTHONUNBUFFERED": "1"},
        timeout=3600
    )
    return result.returncode == 0

def get_pending_drafts(agent_path, count, max_words=0):
    """找出 draft 中还没完成 post 的文件夹（跳过.DS_Store等）
    max_words: 最大字数限制，0=不限
    """
    draft_dir = os.path.join(agent_path, "draft")
    post_dir = os.path.join(agent_path, "post")

    pending = []
    for d in sorted(os.listdir(draft_dir)):
        full_draft = os.path.join(draft_dir, d)
        if not os.path.isdir(full_draft):
            continue
        if d == ".DS_Store" or d.startswith("."):
            continue
        # draft里必须有source.md
        src = os.path.join(full_draft, "source.md")
        if not os.path.exists(src):
            continue
        # 字数限制
        if max_words > 0 and len(open(src).read()) > max_words:
            continue
        # post里没有content.md 或 content.md < 5000字
        content_file = os.path.join(post_dir, d, "content.md")
        if not os.path.exists(content_file) or len(open(content_file).read()) < 5000:
            pending.append(d)

    return pending[:count]

def verify_post(post_full):
    """验证三件套完整性"""
    has_content = os.path.exists(os.path.join(post_full, "content.md"))
    has_cover = os.path.exists(os.path.join(post_full, "cover.png"))
    body_dir = os.path.join(post_full, "body_pages")
    has_body = os.path.isdir(body_dir) and len([f for f in os.listdir(body_dir) if f.endswith('.png')]) > 0
    return has_content and has_cover and has_body

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, required=True)
    parser.add_argument("--max-words", type=int, default=0, help="最大字数限制，0=不限")
    args = parser.parse_args()

    agent_path = resolve_agent_dir(REPO, "onehu-zhihu")

    print(f"🚀 知乎盐选素材一条龙 - 补充 {args.count} 篇")
    print(f"   流程: salt_rewrite → cover_generator → body_image_generator")
    print()

    # 先找出所有待处理的draft
    pending = get_pending_drafts(agent_path, args.count, max_words=args.max_words)
    print(f"   待处理: {len(pending)} 篇\n")

    if not pending:
        print("❌ 没有待处理的draft")
        sys.exit(1)

    success = 0
    failed = 0

    for i, folder_name in enumerate(pending):
        print(f"\n{'='*60}")
        print(f"📦 第 {i+1}/{len(pending)} 篇: {folder_name[:50]}")
        print(f"{'='*60}")

        # Step 1: 仿写
        print(f"\n  📝 Step 1: 仿写")
        ok = run(f"python3 -u scripts/salt_rewrite.py --agent onehu-zhihu --folder '{folder_name}'")
        if not ok:
            print(f"  ❌ 仿写失败")
            failed += 1
            continue

        # Step 2: 封面
        print(f"\n  🎨 Step 2: 封面")
        ok = run(f"python3 -u scripts/cover_generator.py --agent onehu-zhihu --folder '{folder_name}'")
        if not ok:
            print(f"  ❌ 封面失败")
            failed += 1
            continue

        # Step 3: 正文图片
        print(f"\n  📖 Step 3: 正文图片")
        ok = run(f"python3 -u scripts/body_image_generator.py --agent onehu-zhihu --folder '{folder_name}'")
        if not ok:
            print(f"  ❌ 正文图片失败")
            failed += 1
            continue

        # 验证三件套
        post_full = os.path.join(agent_path, "post", folder_name)
        if verify_post(post_full):
            print(f"\n  ✅ 三件套完整！")
            success += 1
            # 删掉已处理的 draft
            draft_full = os.path.join(agent_path, "draft", folder_name)
            if os.path.isdir(draft_full):
                shutil.rmtree(draft_full)
                print(f"  🗑️ 已删除 draft: {folder_name[:50]}")
        else:
            print(f"\n  ❌ 三件套不完整")
            failed += 1

    print(f"\n{'='*60}")
    print(f"🏁 完成！成功 {success}，失败 {failed}")

if __name__ == "__main__":
    main()
