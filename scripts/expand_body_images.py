#!/usr/bin/env python3
"""
对已生成的 post 扩展正文图片池：重拉原文 → 下载 N 张 → 启发式过滤 → 选 Top-3 替换 02/03/04。

适用场景：原文图片密度高（>10 张），Top-3 选择池太小导致 body 图片不够多样。

下载后过滤（fetch_rss.py 预过滤之外）：
  1. perceptual hash 相似度 > 0.85 视为重复
  2. 像素方差 < 阈值视为空白/纯色
  3. 文件 < 8KB 视为损坏
  4. 尺寸 < 400px 任一边视为缩略图

用法:
  python3 expand_body_images.py --agent-slug susu-fashion --item-id 3550746681-2247610725_1
  python3 expand_body_images.py --agent-slug susu-fashion --all --top-n 12
"""
import argparse, os, sys, json, re, html, shutil, tempfile, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

WEMPRSS_BASE = "https://wemprss.twoice.fun:666"
FARM_ROOT = Path(os.path.expanduser("~/phanthy-farm"))
USER_AGENT = "Mozilla/5.0 (PhanthyFarm/1.0)"

# 复用 fetch_rss.py 的 URL 启发式排除规则
URL_EXCLUDE = [
    "qrcode", "qr_noroaming", "biz_qr", "mmbiz_qrcode",  # 二维码
    "biz_head", "headimg",                                # 名片
    "placeholder", "default_cover",                       # 占位
]

MIN_FILE_SIZE = 8000       # 8KB 以下视为损坏
MIN_DIM = 400              # 任一边 < 400 视为缩略图
BLANK_STD_THRESHOLD = 8.0  # 像素灰度标准差 < 8 视为纯色/空白
PHASH_HAMMING_MAX = 8      # 64-bit pHash 距离 ≤ 8 视为重复


def fetch_rss(mp_id: str, limit: int = 30) -> str:
    url = f"{WEMPRSS_BASE}/rss/{mp_id}?limit={limit}&offset=0"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse_rss(xml: str) -> dict:
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml)
    ns = {"content": "http://purl.org/rss/1.0/modules/content/"}
    channel = root.find("channel")
    items = []
    for it in channel.findall("item"):
        item = {
            "id": (it.findtext("id") or "").strip(),
            "title": (it.findtext("title") or "").strip(),
            "cover_url": "",
        }
        enc = it.find("enclosure")
        if enc is not None:
            item["cover_url"] = enc.attrib.get("url", "")
        # 解析 content:encoded 里的所有 <img>
        content = (it.find("content:encoded", ns).text
                   if it.find("content:encoded", ns) is not None else "")
        images = []
        for m in re.finditer(r'<img[^>]+src="([^"]+)"([^>]*)>', content):
            url = html.unescape(m.group(1))
            attrs = m.group(2)
            alt_m = re.search(r'alt="([^"]*)"', attrs)
            w_m = re.search(r'width="(\d+)"', attrs)
            h_m = re.search(r'height="(\d+)"', attrs)
            images.append({
                "url": url,
                "alt": alt_m.group(1) if alt_m else "",
                "width": int(w_m.group(1)) if w_m else None,
                "height": int(h_m.group(1)) if h_m else None,
            })
        item["images"] = images
        items.append(item)
    return {"mp_name": (channel.findtext("title") or "").strip(), "items": items}


def url_excluded(url: str) -> Optional[str]:
    u = url.lower()
    for kw in URL_EXCLUDE:
        if kw in u:
            return f"URL 命中排除规则: {kw}"
    if u.endswith(".gif") or "mmbiz_gif" in u:
        return "GIF 表情"
    return None


def score(img: dict, pos: int) -> int:
    """沿用 fetch_rss.pick_top3_images 的打分逻辑。"""
    s = 0
    u = img["url"].lower()
    w, h = img.get("width"), img.get("height")
    if w and h:
        if w >= 600 and h >= 400:
            s += 3
        ratio = w / h if h else 0
        if any(abs(ratio - r) < 0.15 * r for r in [16/9, 4/3, 1.0, 3/2]):
            s += 2
    if "mmbiz_jpg" in u or "mmbiz_png" in u:
        s += 1
    if pos >= 1:
        s += 1
    if img.get("alt") and "广告" not in img["alt"]:
        s += 1
    if any(k in u for k in ["640", "article", "content"]):
        s += 1
    return s


def proxy_download(img_url: str, dst: Path, crop_bottom: float = 0.20):
    """复用 fetch_rss.proxy_download 的下载 + 裁水印逻辑。"""
    proxy = f"{WEMPRSS_BASE}/api/v1/wx/tools/image/proxy?" + \
            urllib.parse.urlencode({"url": img_url, "output_format": "jpeg"})
    req = urllib.request.Request(proxy, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw_bytes = resp.read()

    if crop_bottom <= 0:
        dst.write_bytes(raw_bytes)
        return

    try:
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(raw_bytes))
        w, h = im.size
        crop_h = int(h * crop_bottom)
        cropped = im.crop((0, 0, w, h - crop_h))
        if cropped.mode in ("RGBA", "P"):
            cropped = cropped.convert("RGB")
        cropped.save(dst, "JPEG", quality=92, optimize=True)
    except Exception as e:
        sys.stderr.write(f"[warn] crop failed for {dst.name}: {e}\n")
        dst.write_bytes(raw_bytes)


def phash(img_path: Path) -> Optional[int]:
    """64-bit perceptual hash (8x8 average hash, 简化版)。"""
    try:
        from PIL import Image
        im = Image.open(img_path).convert("L").resize((8, 8), Image.LANCZOS)
        pixels = list(im.getdata())
        avg = sum(pixels) / 64
        bits = "".join("1" if p > avg else "0" for p in pixels)
        return int(bits, 2)
    except Exception:
        return None


def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def is_blank(img_path: Path) -> bool:
    """纯色/空白检测：灰度标准差 < 阈值。"""
    try:
        from PIL import Image
        im = Image.open(img_path).convert("L")
        # 缩到 200x200 加速计算
        im_small = im.resize((200, 200), Image.LANCZOS)
        pixels = list(im_small.getdata())
        n = len(pixels)
        mean = sum(pixels) / n
        var = sum((p - mean) ** 2 for p in pixels) / n
        std = var ** 0.5
        return std < BLANK_STD_THRESHOLD
    except Exception:
        return False


def post_download_filter(downloaded: list[tuple[Path, dict, int]]) -> list[tuple[Path, dict, int]]:
    """下载后过滤：去重 + 空白 + 损坏 + 缩略图。"""
    keep = []
    seen_hashes = []
    for path, img, s in downloaded:
        if not path.exists():
            continue
        size = path.stat().st_size
        if size < MIN_FILE_SIZE:
            print(f"  [skip] {path.name}: 文件 {size} B (<{MIN_FILE_SIZE})")
            continue
        # 尺寸
        try:
            from PIL import Image
            im = Image.open(path)
            w, h = im.size
            if w < MIN_DIM or h < MIN_DIM:
                print(f"  [skip] {path.name}: 尺寸 {w}x{h} (<{MIN_DIM})")
                continue
        except Exception:
            print(f"  [skip] {path.name}: 无法打开")
            continue
        # 空白
        if is_blank(path):
            print(f"  [skip] {path.name}: 空白/纯色")
            continue
        # pHash 去重
        h_phash = phash(path)
        if h_phash is not None:
            dup = any(hamming(h_phash, hp) <= PHASH_HAMMING_MAX for hp in seen_hashes)
            if dup:
                print(f"  [skip] {path.name}: pHash 重复")
                continue
            seen_hashes.append(h_phash)
        keep.append((path, img, s))
    return keep


def expand_post(agent_slug: str, item_id: str, post_dir: Path, top_n: int = 12):
    """对一个 post 重新下载更多图片 + 过滤 + 选 Top-3 替换 02/03/04。"""
    print(f"\n=== {post_dir.name} (item_id={item_id}) ===")
    if not post_dir.exists():
        print(f"  [err] post 目录不存在: {post_dir}")
        return False

    # 1. 从 post_dir 的 source_orig_url 反查 mp_id (从 manifest 读)
    manifest_path = post_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"  [err] manifest.json 缺失")
        return False
    manifest = json.loads(manifest_path.read_text())
    source_url = manifest.get("source_orig_url", "")
    if not source_url:
        print(f"  [err] manifest 缺 source_orig_url")
        return False

    # 2. 解析 mp_id — item_id 格式为 "<num>-<article_id>"，mp_id = MP_WXS_<num>
    # 不调 by_article API（容易 50001）
    mp_num = item_id.split("-", 1)[0]
    mp_id = f"MP_WXS_{mp_num}"
    print(f"  mp_id={mp_id} (从 item_id 解析)")

    # 3. 拉 RSS 找该 article 的 images
    xml = fetch_rss(mp_id, limit=30)
    parsed = parse_rss(xml)
    target = next((it for it in parsed["items"] if it["id"] == item_id), None)
    if not target:
        print(f"  [err] item_id={item_id} 不在 RSS 里")
        return False
    images = target["images"]
    cover_url = target["cover_url"]
    print(f"  原文 {len(images)} 张图 (cover 1 + body {len(images)-1 if len(images)>0 else 0})")

    # 4. URL 启发式排除
    candidates = []
    for pos, img in enumerate(images):
        reason = url_excluded(img["url"])
        if reason:
            continue
        # 排除封面本身
        if cover_url and urlparse(img["url"]).path == urlparse(cover_url).path:
            continue
        candidates.append((score(img, pos), pos, img))
    candidates.sort(key=lambda x: (-x[0], x[1]))
    print(f"  启发式过滤后: {len(candidates)} 张候选")
    if not candidates:
        print(f"  [err] 无可用候选")
        return False

    # 5. 下载 top_n 张
    pool = candidates[:top_n]
    print(f"  下载 Top-{len(pool)} 张到临时目录...")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        downloaded = []
        for i, (s, pos, img) in enumerate(pool):
            dst = tmp_dir / f"img_{i:02d}_s{s}.jpg"
            try:
                proxy_download(img["url"], dst)
                downloaded.append((dst, img, s))
            except Exception as e:
                print(f"    [skip] 下载失败: {e}")
        print(f"  下载完成: {len(downloaded)}/{len(pool)}")

        # 6. 下载后过滤
        filtered = post_download_filter(downloaded)
        print(f"  过滤后保留: {len(filtered)} 张")

        # 7. 取 Top-3
        if len(filtered) < 3:
            print(f"  [err] 过滤后不足 3 张 ({len(filtered)})，保留现有 02/03/04")
            return False
        top3 = filtered[:3]
        print(f"  选 Top-3: 分数 {[t[2] for t in top3]}")

        # 8. 备份原 02/03/04 + 替换
        backup_dir = post_dir / ".expand_backup"
        backup_dir.mkdir(exist_ok=True)
        for n in [1, 2, 3]:
            src = post_dir / f"0{n+1}.jpg"
            if src.exists():
                shutil.copy2(src, backup_dir / f"0{n+1}.jpg")
        for n, (path, img, s) in enumerate(top3, start=1):
            dst = post_dir / f"0{n+1}.jpg"
            shutil.copy2(path, dst)
            print(f"  替换 0{n+1}.jpg ({path.stat().st_size} B)")

        # 9. 更新 manifest.json 的 source_rank
        # 重新读出来重写
        manifest["images"][2]["source_rank"] = 1  # body_1 → rank 1
        manifest["images"][3]["source_rank"] = 2  # body_2 → rank 2
        manifest["images"][4]["source_rank"] = 3  # body_3 → rank 3
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  manifest.json source_rank 更新")
        return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent-slug", required=True)
    ap.add_argument("--item-id", help="单个 article item_id")
    ap.add_argument("--post-dir", help="post 目录路径（与 --item-id 配合）")
    ap.add_argument("--all", action="store_true", help="对 agent 下所有 pending_post 跑")
    ap.add_argument("--top-n", type=int, default=12, help="下载 Top-N 张（默认 12）")
    args = ap.parse_args()

    if args.all:
        agent_dir = FARM_ROOT / "agents" / args.agent_slug
        pending = agent_dir / "pending_posts"
        for post_dir in sorted(pending.iterdir()):
            if not post_dir.is_dir():
                continue
            manifest_path = post_dir / "manifest.json"
            if not manifest_path.exists():
                continue
            m = json.loads(manifest_path.read_text())
            item_id = m.get("source_item_id", "")
            if item_id:
                expand_post(args.agent_slug, item_id, post_dir, top_n=args.top_n)
    else:
        if not args.item_id or not args.post_dir:
            ap.error("--item-id 和 --post-dir 必填（除非 --all）")
        expand_post(args.agent_slug, args.item_id, Path(args.post_dir), top_n=args.top_n)


if __name__ == "__main__":
    main()
