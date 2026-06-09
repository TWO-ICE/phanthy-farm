#!/usr/bin/env python3
"""
从 wemprss 拉取博主 RSS，清洗为标准化 Markdown 选题库。

v3: 正文图片全部下载（排除异常/小图/二维码/GIF），下载后裁下方 20% 去水印。

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
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", raw_html, flags=re.S|re.I)
    images = []
    raw_matches = list(re.finditer(r'<img[^>]+src="([^"]+)"([^>]*)>', raw))
    for m in raw_matches:
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


def filter_body_images(images: list, cover_url: str = "") -> list:
    """
    v3: 筛选所有正文配图（不限数量），排除异常。
    排除规则：二维码、公众号名片、占位图、小尺寸(<200x200)、GIF、广告图、比例异常(<0.3 或 >5)。
    """
    def exclude(img):
        u = img["url"].lower()
        alt = (img.get("alt") or "").lower()
        # 二维码
        if any(k in u for k in ["qrcode", "qr_noroaming", "biz_qr", "mmbiz_qrcode"]):
            return "二维码"
        # 公众号名片
        if any(k in u for k in ["biz_head", "headimg"]):
            return "公众号名片"
        # 占位图
        if any(k in u for k in ["placeholder", "default_cover"]):
            return "占位图"
        # 尺寸检查
        w, h = img.get("width"), img.get("height")
        if w and h:
            if w < 200 or h < 200:
                return f"小尺寸({w}x{h})"
            ratio = w / h
            if ratio < 0.3 or ratio > 5:
                return f"比例异常({ratio:.1f})"
        # GIF
        if u.endswith(".gif") or "mmbiz_gif" in u:
            return "GIF"
        # 广告
        if any(k in alt for k in ["广告", "banner", "推广"]):
            return "广告"
        # 推广类图片（常见于底部）
        if any(k in u for k in ["biz_tpc", "reward", "zan", "like"]):
            return "推广图"
        return None

    def score(img, pos):
        s = 0
        u = img["url"].lower()
        w, h = img.get("width"), img.get("height")
        if w and h:
            if w >= 600 and h >= 400: s += 3
            elif w >= 400 and h >= 300: s += 1
        if "mmbiz_jpg" in u or "mmbiz_png" in u: s += 1
        if pos >= 1: s += 1  # 跳过第一张（可能是封面重复）
        if img.get("alt"): s += 1
        if any(k in u for k in ["640", "article", "content"]): s += 1
        return s

    scored = []
    for pos, img in enumerate(images):
        reason = exclude(img)
        if reason:
            continue
        # 跳过和封面一样的图
        if cover_url:
            from urllib.parse import urlparse
            iu = urlparse(img["url"]).path.split("/")[-1].split("?")[0]
            cu = urlparse(cover_url).path.split("/")[-1].split("?")[0]
            if iu and cu and iu == cu:
                continue
        s = score(img, pos)
        scored.append((s, pos, img))

    # 按分数排序，但保持原文顺序（stable sort by position）
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [item[2] for item in scored]


def remove_noise(text):
    noise = [
        r"点亮[^\n]*关注", r"点个[^\n]*赞", r"转发[^\n]*支持", r"收藏[^\n]*不迷路",
        r"主页[^\n]*更多", r"求[^\n]*三连", r"扫码[^\n]*关注", r"长按[^\n]*识别",
        r"本文[^\n]*作者", r"商务[^\n]*合作", r"来源[^\n]*网络",
    ]
    for pat in noise:
        text = re.sub(pat, "", text, flags=re.I)
    return re.sub(r"\n{3,}", "\n\n", text).strip()

def parse_pubdate(s):
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(s).strftime("%Y-%m-%d")
    except:
        return s[:10] if len(s) >= 10 else s

def proxy_download(url: str, dst: Path, crop_bottom: float = 0.20):
    """通过 wemprss 图片代理下载，自动裁剪下方 crop_bottom（默认 20%）去水印。"""
    dl_url = f"{WEMPRSS_BASE}/api/v1/wx/image-proxy?url={urllib.parse.quote(url, safe='')}"
    req = urllib.request.Request(dl_url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw_bytes = resp.read()

    if not raw_bytes or len(raw_bytes) < 500:
        raise RuntimeError(f"empty response ({len(raw_bytes)} bytes)")

    dst.parent.mkdir(parents=True, exist_ok=True)

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

    print(f"[1/4] Fetching RSS for {args.mp_id} (top {args.top_n})")
    xml = fetch_rss(args.mp_id, args.top_n)
    parsed = parse_rss(xml)
    print(f"     mp_name={parsed['mp_name']}, items={len(parsed['items'])}")

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

                # v3: 正文配图全下载（排除异常），不再限 3 张
                body_images = filter_body_images(images, it.get("cover_url", ""))
                rec["body_images"] = []
                for n, pick in enumerate(body_images, start=1):
                    dst = item_dir / f"img_{n}.jpg"
                    entry = {"rank": n, "url": pick["url"],
                             "alt": pick.get("alt", ""),
                             "file": f"img_{n}.jpg"}
                    try:
                        proxy_download(pick["url"], dst)
                        entry["status"] = "ok"
                    except Exception as e:
                        entry["status"] = f"failed: {e}"
                    rec["body_images"].append(entry)
                rec["body_image_count"] = len(body_images)
                rec["body_image_failed"] = sum(1 for e in rec["body_images"] if e["status"] != "ok")

            front = "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False) if not isinstance(v,str) else v}"
                              for k, v in rec.items())
            md = f"---\n{front}\n---\n\n{text}"
            (raw_dir / f"{it['id']}.md").write_text(md)

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
