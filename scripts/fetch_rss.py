#!/usr/bin/env python3
"""
从 wemprss 拉取博主 RSS，清洗为标准化 Markdown 选题库。

用法:
  python3 fetch_rss.py --mp-id MP_WXS_xxx --agent-slug linajie --top-n 20
"""
import argparse, os, sys, json, re, html, time
from datetime import datetime
from pathlib import Path
import urllib.request, urllib.parse

WEMPRSS_BASE = "https://wemprss.twoice.fun:666"
FARM_ROOT = Path(os.path.expanduser("~/phanthy-farm"))
USER_AGENT = "Mozilla/5.0 (PhanthyFarm/1.0)"

def fetch_rss(mp_id: str, top_n: int) -> str:
    url = f"{WEMPRSS_BASE}/rss/{mp_id}?limit={top_n}&offset=0"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")

def parse_rss(xml: str) -> dict:
    """简易 RSS 解析（无依赖）。"""
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml)
    ns = {"content": "http://purl.org/rss/1.0/modules/content/"}
    channel = root.find("channel")
    items = []
    for it in channel.findall("item"):
        item = {
            "id": (it.findtext("id") or "").strip(),
            "title": (it.findtext("title") or "").strip(),
            "pubDate": (it.findtext("pubDate") or "").strip(),
            "guid": (it.findtext("guid") or "").strip(),
            "description": (it.findtext("description") or "").strip(),
            "content_encoded": (it.find("content:encoded", ns).text
                                 if it.find("content:encoded", ns) is not None else ""),
        }
        enc = it.find("enclosure")
        if enc is not None:
            item["cover_url"] = enc.attrib.get("url", "")
        items.append(item)
    return {
        "mp_name": (channel.findtext("title") or "").strip(),
        "mp_desc": (channel.findtext("description") or "").strip(),
        "mp_avatar": (channel.find("image").findtext("url")
                       if channel.find("image") is not None else ""),
        "items": items,
    }

def clean_html(raw_html: str):
    """返回 (纯文本, 图片列表)。图片 URL 已解码 &amp; → &。"""
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", raw_html, flags=re.S|re.I)
    images = []
    raw_matches = list(re.finditer(r'<img[^>]+src="([^"]+)"([^>]*)>', raw))
    for m in raw_matches:
        url = html.unescape(m.group(1))  # 解码 &amp; → &
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
    # 替换 <img> 为占位符（用原始匹配，避免解码后 escape 失配）
    for idx in range(len(raw_matches) - 1, -1, -1):
        m = raw_matches[idx]
        raw = raw[:m.start()] + f"\n[IMG:{idx}]\n" + raw[m.end():]
    text = re.sub(r"</(p|div|h[1-6]|li|br)>", "\n", raw, flags=re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip(), images


def pick_top3_images(images: list, cover_url: str = "") -> list:
    """按 prompts/00 § 4.2-4.3 规则筛 Top-3 正文配图。"""
    from urllib.parse import urlparse

    def exclude(img):
        u = img["url"].lower()
        alt = (img.get("alt") or "").lower()
        if any(k in u for k in ["qrcode", "qr_noroaming", "biz_qr", "mmbiz_qrcode"]):
            return "二维码"
        if any(k in u for k in ["biz_head", "headimg"]):
            return "公众号名片"
        if any(k in u for k in ["placeholder", "default_cover"]):
            return "占位图"
        # 注意：watermark=1 是微信全图水印参数，不视作"水印占位"
        w, h = img.get("width"), img.get("height")
        if w and h and (w < 200 or h < 200):
            return f"小尺寸({w}x{h})"
        if u.endswith(".gif") or "mmbiz_gif" in u:
            return "GIF表情"
        if any(k in alt for k in ["广告", "banner"]):
            return "广告"
        return None

    def score(img, pos):
        s = 0
        u = img["url"].lower()
        w, h = img.get("width"), img.get("height")
        if w and h:
            if w >= 600 and h >= 400: s += 3
            ratio = w / h if h else 0
            if any(abs(ratio - r) < 0.15 * r for r in [16/9, 4/3, 1.0, 3/2]):
                s += 2
        if "mmbiz_jpg" in u or "mmbiz_png" in u: s += 1
        if pos >= 1: s += 1
        if img.get("alt") and "广告" not in img["alt"]: s += 1
        if any(k in u for k in ["640", "article", "content"]): s += 1
        return s

    scored = []
    for pos, img in enumerate(images):
        if exclude(img):
            continue
        if cover_url and urlparse(img["url"]).path == urlparse(cover_url).path:
            continue
        scored.append((score(img, pos), pos, img))

    scored.sort(key=lambda x: (-x[0], x[1]))
    return [item[2] for item in scored[:3]]

NOISE_PATTERNS = [
    r"点亮关注", r"点赞收藏", r"求个三连", r"主页看更多", r"求关注",
    r"在看|星标|转发|收藏", r"上篇|下篇|往期",
]

def remove_noise(text: str) -> str:
    for pat in NOISE_PATTERNS:
        text = re.sub(pat, "", text)
    return text

def parse_pubdate(s: str) -> str:
    try:
        return datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d")
    except Exception:
        return ""

def proxy_download(img_url: str, dst: Path, crop_bottom: float = 0.20):
    """
    下载图片并裁剪下方 crop_bottom 比例（默认 20%），用于去掉公众号水印。
    crop_bottom=0 表示不裁剪。
    """
    proxy = f"{WEMPRSS_BASE}/api/v1/wx/tools/image/proxy?" + \
            urllib.parse.urlencode({"url": img_url, "output_format": "jpeg"})
    req = urllib.request.Request(proxy, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw_bytes = resp.read()

    if crop_bottom <= 0:
        dst.write_bytes(raw_bytes)
        return

    # 裁剪下方 crop_bottom 区域
    try:
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(raw_bytes))
        w, h = im.size
        crop_h = int(h * crop_bottom)
        # 保留上方 (0, 0) 到 (w, h - crop_h)
        cropped = im.crop((0, 0, w, h - crop_h))
        # 保存为 JPEG 格式
        if cropped.mode in ("RGBA", "P"):
            cropped = cropped.convert("RGB")
        cropped.save(dst, "JPEG", quality=92, optimize=True)
    except Exception as e:
        # PIL 不可用或图片损坏 → 保留原图
        sys.stderr.write(f"[warn] crop failed for {dst.name}: {e}, saving original\n")
        dst.write_bytes(raw_bytes)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mp-id", required=True)
    ap.add_argument("--agent-slug", required=True)
    ap.add_argument("--top-n", type=int, default=20)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    agent_dir = FARM_ROOT / "agents" / args.agent_slug
    sources = agent_dir / "sources"
    raw_dir = sources / "raw"
    if not args.dry_run:
        raw_dir.mkdir(parents=True, exist_ok=True)

    # 1. 拉取
    print(f"[1/4] Fetching RSS for {args.mp_id} (top {args.top_n})")
    xml = fetch_rss(args.mp_id, args.top_n)
    parsed = parse_rss(xml)
    print(f"     mp_name={parsed['mp_name']}, items={len(parsed['items'])}")

    # 2. 元数据
    meta = {
        "mp_id": args.mp_id,
        "mp_name": parsed["mp_name"],
        "mp_desc": parsed["mp_desc"],
        "mp_avatar": parsed["mp_avatar"],
        "fetched_at": datetime.now().strftime("%Y-%m-%d"),
        "agent_slug": args.agent_slug,
    }
    if not args.dry_run:
        (sources / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))

    # 3. 清洗 + 落盘
    valid, skipped = [], []
    for it in parsed["items"]:
        if not it["id"]: continue
        text, images = clean_html(it["content_encoded"])
        text = remove_noise(text)
        char_count = len(text)
        item_dir = raw_dir / it["id"]
        rec = {
            "item_id": it["id"], "mp_id": args.mp_id,
            "mp_name": parsed["mp_name"], "title": it["title"],
            "pub_date": parse_pubdate(it["pubDate"]),
            "orig_url": it["guid"],
            "cover_status": "pending", "cover_local": "",
            "char_count": char_count, "skipped": char_count < 300,
            "images_in_text": len(images),
        }
        if char_count < 300:
            skipped.append((it["id"], char_count))
            rec["cover_status"] = "skipped"
        else:
            valid.append((it["id"], char_count))

        if not args.dry_run:
            if not rec["skipped"]:
                item_dir.mkdir(parents=True, exist_ok=True)
                rec["cover_local"] = f"sources/raw/{it['id']}/cover.jpg"
                try:
                    proxy_download(it["cover_url"], item_dir / "cover.jpg")
                    rec["cover_status"] = "ok"
                except Exception as e:
                    rec["cover_status"] = f"failed: {e}"

                # 正文配图：JPG 优先，GIF/小尺寸/二维码排除，取 Top-3
                top3 = pick_top3_images(images, it.get("cover_url", ""))
                rec["top3_images"] = []
                for n, pick in enumerate(top3, start=1):
                    dst = item_dir / f"img_{n}.jpg"
                    entry = {"rank": n, "url": pick["url"],
                             "alt": pick.get("alt", ""),
                             "file": f"img_{n}.jpg"}
                    try:
                        proxy_download(pick["url"], dst)
                        entry["status"] = "ok"
                    except Exception as e:
                        entry["status"] = f"failed: {e}"
                    rec["top3_images"].append(entry)
                # 不足 3 张：由阶段 3 调 $gemini-image 补足（此处不调，仅记缺口）
                rec["top3_gap"] = max(0, 3 - len(top3))

            front = "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False) if not isinstance(v,str) else v}"
                              for k, v in rec.items())
            md = f"---\n{front}\n---\n\n{text}"
            (raw_dir / f"{it['id']}.md").write_text(md)

    # 4. 打包
    if not args.dry_run and valid:
        import zipfile
        zip_path = sources / f"{args.mp_id}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in sources.rglob("*"):
                if p.is_file() and p != zip_path:
                    zf.write(p, p.relative_to(sources))
        print(f"[4/4] Zipped → {zip_path}")

    print(f"\n[Done] valid={len(valid)}, skipped={len(skipped)}")
    if skipped:
        print("跳过（字数<300）:")
        for iid, c in skipped[:5]:
            print(f"  - {iid}: {c} 字")

if __name__ == "__main__":
    main()
