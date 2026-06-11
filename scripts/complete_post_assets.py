#!/usr/bin/env python3
"""为已有的 post 补齐封面和正文图。
用法: python3 complete_post_assets.py --agent onehu-zhihu
"""
import argparse, os, re, sys, urllib.request
from pathlib import Path

REPO = Path("/Users/4paradigm/Documents/phanthy")

# 把 _lib.py 的目录加进来
sys.path.insert(0, str(REPO / "scripts"))
from _lib import (
    parse_image_urls_from_markdown, filter_candidates,
    download_and_crop, post_download_filter,
)
from PIL import Image


def make_cover(img_path: Path, out_path: Path, target_w=896, target_h=1200):
    """居中裁剪为封面尺寸"""
    img = Image.open(img_path)
    w, h = img.size
    ratio = target_w / target_h
    img_ratio = w / h
    if img_ratio > ratio:
        new_w = int(h * ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    img = img.resize((target_w, target_h), Image.LANCZOS)
    img.save(out_path, "PNG")
    return img.size


def process_one(post_dir: Path, draft_dir: Path):
    """处理单个 post 目录，返回 (补了封面, 正文图数)"""
    name = post_dir.name
    content_file = post_dir / "content.md"
    if not content_file.exists():
        return False, 0

    # 找对应的 draft（支持子目录模式 draft/post_XXX/source.md 和文件模式 draft/post_XXX.md）
    draft_file = None
    candidate_dir = draft_dir / name
    if (candidate_dir / "source.md").exists():
        draft_file = candidate_dir / "source.md"
    elif (draft_dir / f"{name}.md").exists():
        draft_file = draft_dir / f"{name}.md"
    if not draft_file:
        print(f"  ⚠️ 找不到 draft: {name}")
        return False, 0

    with open(draft_file) as f:
        md = f.read()

    # === 封面 ===
    cover_path = post_dir / "cover.png"
    cover_done = cover_path.exists()
    if not cover_done:
        m = re.search(r'!\[.*?\]\((https?://[^\s\)]+)\)', md)
        if m:
            tmp = Path(f"/tmp/cover_{name}.jpg")
            try:
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                opener.addheaders = [("User-Agent", "Mozilla/5.0")]
                resp = opener.open(m.group(1), timeout=30)
                tmp.write_bytes(resp.read())
                make_cover(tmp, cover_path)
                cover_done = True
                print(f"  🖼️ 封面 ✅")
                tmp.unlink(missing_ok=True)
            except Exception as e:
                print(f"  🖼️ 封面 ❌: {e}")

    # === 正文图 ===
    body_dir = post_dir / "body_pages"
    existing = list(body_dir.glob("*.jpg")) if body_dir.exists() else []
    if len(existing) > 0:
        return cover_done, len(existing)

    body_dir.mkdir(parents=True, exist_ok=True)
    images = parse_image_urls_from_markdown(md)
    cover_url = images[0]["url"] if images else ""
    candidates = filter_candidates(images, cover_url)

    downloaded = []
    for score, pos, img in candidates:
        path = body_dir / f"page_{len(downloaded)+1:03d}.jpg"
        ok = download_and_crop(img["url"], path)
        if ok:
            downloaded.append(path)

    # 二级过滤
    seen_hashes = []
    kept = []
    for f in sorted(body_dir.glob("*.jpg")):
        reason = post_download_filter(f, seen_hashes)
        if reason:
            f.unlink()
        else:
            kept.append(f)

    print(f"  📸 正文图: {len(images)}张 → {len(kept)}张")
    return cover_done, len(kept)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True)
    args = parser.parse_args()

    agent_dir = REPO / "agents" / args.agent
    post_dir = agent_dir / "post"
    draft_dir = agent_dir / "draft"

    if not post_dir.exists():
        print(f"❌ post 目录不存在: {post_dir}")
        sys.exit(1)

    posts = sorted([d for d in post_dir.iterdir() if d.is_dir()])
    print(f"📋 共 {len(posts)} 个 post 目录\n")

    done = 0
    for p in posts:
        print(f"📝 {p.name}")
        cover_ok, body_count = process_one(p, draft_dir)
        if cover_ok and body_count > 0:
            done += 1
        print()

    print(f"🏁 完成！完整素材包: {done}/{len(posts)}")


if __name__ == "__main__":
    main()
