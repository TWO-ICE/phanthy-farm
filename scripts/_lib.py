"""
phanthy-farm scripts 共享库 — 图片下载/过滤/裁剪 通用规则

【v3 通用规则】对所有 agent 适用：
  1. URL 启发式排除：二维码 / 公众号名片 / 占位图 / GIF / 推广图
  2. 比例异常排除：w/h < 0.3（竖向极窄）或 > 5（横向横幅）
  3. 下载后过滤：< 8KB / 尺寸 < 400px / 空白纯色 / pHash 重复
  4. 下载后裁剪：裁下方 20% 去公众号水印
  5. 封面排除：与 cover URL basename 相同的图跳过

用法:
  from _lib import download_body_image, filter_candidates
  candidates = filter_candidates(images, cover_url)
  for c in candidates:
      download_body_image(c['url'], dst_path)
"""
import os, re, sys, io, hashlib
import urllib.request, urllib.parse, ssl
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
from PIL import Image

# === 通用配置 ===
WEMPRSS_BASE = os.environ.get("WEMPRSS_BASE", "https://wemprss.twoice.fun:666")
USER_AGENT = "Mozilla/5.0 (PhanthyFarm/1.0)"

# 下载设置
MIN_FILE_SIZE = 8000       # 8KB 以下视为损坏
MIN_DIM = 300              # 任一边 < 300 视为缩略图（400 会误杀 16:9 产品图如 640x342）
BLANK_STD_THRESHOLD = 8.0  # 像素灰度标准差 < 8 视为纯色/空白
PHASH_HAMMING_MAX = 8      # 64-bit pHash 距离 ≤ 8 视为重复
CROP_BOTTOM = 0.20         # 裁下方 20% 去公众号水印

# 比例异常阈值
RATIO_MIN = 0.3   # 比例 < 0.3 视为极窄（竖向广告条）
RATIO_MAX = 5.0   # 比例 > 5.0 视为极宽（横幅步骤图）

# URL 启发式排除规则
URL_EXCLUDE_KEYWORDS = [
    "qrcode", "qr_noroaming", "biz_qr", "mmbiz_qrcode",  # 二维码
    "biz_head", "headimg",                                # 公众号名片
    "placeholder", "default_cover",                       # 占位图
    "biz_tpc", "reward", "zan", "like",                   # 推广图
]

# 上下文推广关键词（出现在图片前后文中的 → 排除该图片）
PROMO_CONTEXT_KEYWORDS = [
    "合作联系", "加微信", "加个人微信", "扫码关注", "关注公众号",
    "长按关注", "二维码关注", "关注我们", "商务合作", "投稿合作",
    "联系小编", "加入社群", "进群", "添加好友", "微信号",
    "更多精彩", "推荐阅读", "往期回顾", "热文推荐",
]

# === SSL context（避免 wemprss 证书问题） ===
_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE


# ============================================================
# 一级过滤：URL 启发式 + 比例异常
# ============================================================
def is_excluded_url(url: str) -> Optional[str]:
    """URL 启发式排除。返回 reason 或 None。"""
    u = url.lower()
    for kw in URL_EXCLUDE_KEYWORDS:
        if kw in u:
            return f"URL 命中排除: {kw}"
    if u.endswith(".gif") or "mmbiz_gif" in u:
        return "GIF 表情"
    return None


def is_excluded_ratio(width: int, height: int) -> Optional[str]:
    """比例异常排除（横幅/极窄图）。"""
    if not (width and height):
        return None
    if width < 200 or height < 200:
        return f"小尺寸({width}x{height})"
    ratio = width / height
    if ratio < RATIO_MIN:
        return f"比例极窄({ratio:.2f})"
    if ratio > RATIO_MAX:
        return f"比例极宽({ratio:.2f})"
    return None


def filter_candidates(images: list, cover_url: str = "") -> list:
    """
    一级过滤：URL + 比例，返回 (score, position, img_dict) 列表（已排序）。
    img_dict 需含 url, alt, width, height 字段。
    """
    cover_basename = urlparse(cover_url).path.split('/')[-1].split('?')[0] if cover_url else ''

    out = []
    for pos, img in enumerate(images):
        url = img.get('url', '')
        if not url:
            continue
        # 1. URL 启发式
        r = is_excluded_url(url)
        if r:
            continue
        # 2. 比例异常
        r = is_excluded_ratio(img.get('width'), img.get('height'))
        if r:
            continue
        # 3. 跳过封面本身
        if cover_basename:
            ib = urlparse(url).path.split('/')[-1].split('?')[0]
            if ib and ib == cover_basename:
                continue
        # 4. 上下文推广过滤
        if img.get('_promo'):
            continue
        # 5. 打分
        s = score_image(img, pos)
        out.append((s, pos, img))
    # 按分数降序，position 升序
    out.sort(key=lambda x: (-x[0], x[1]))
    return out


def score_image(img: dict, pos: int) -> int:
    """图片质量打分（高=更重要）。"""
    s = 0
    u = img.get('url', '').lower()
    w, h = img.get('width'), img.get('height')
    if w and h:
        if w >= 600 and h >= 400:
            s += 3
        elif w >= 400 and h >= 300:
            s += 1
        # 常见比例加分
        ratio = w / h if h else 0
        if any(abs(ratio - r) < 0.15 * r for r in [16/9, 4/3, 1.0, 3/2]):
            s += 2
    if "mmbiz_jpg" in u or "mmbiz_png" in u:
        s += 1
    if pos >= 1:  # 跳过第一张（可能是封面重复）
        s += 1
    alt = (img.get('alt') or '').lower()
    if alt and "广告" not in alt:
        s += 1
    if any(k in u for k in ["640", "article", "content"]):
        s += 1
    return s


# ============================================================
# 二级过滤：下载后检测（pHash / 空白 / 尺寸 / 文件大小）
# ============================================================
def phash(img_path: Path) -> Optional[int]:
    """64-bit perceptual hash (8x8 average hash, 简化版)。"""
    try:
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
        im = Image.open(img_path).convert("L")
        im_small = im.resize((200, 200), Image.LANCZOS)
        pixels = list(im_small.getdata())
        n = len(pixels)
        mean = sum(pixels) / n
        var = sum((p - mean) ** 2 for p in pixels) / n
        std = var ** 0.5
        return std < BLANK_STD_THRESHOLD
    except Exception:
        return False


def post_download_filter(path: Path, seen_hashes: list) -> Optional[str]:
    """
    下载后过滤：返回 None 表示通过；返回字符串表示被过滤（+ reason）。
    seen_hashes 是当前批次已下载图片的 pHash 列表（函数内部 append）。
    """
    if not path.exists():
        return "文件不存在"
    size = path.stat().st_size
    if size < MIN_FILE_SIZE:
        return f"文件 {size} B < {MIN_FILE_SIZE}"
    try:
        im = Image.open(path)
        w, h = im.size
        if w < MIN_DIM or h < MIN_DIM:
            return f"尺寸 {w}x{h} < {MIN_DIM}"
    except Exception as e:
        return f"无法打开: {e}"
    if is_blank(path):
        return "空白/纯色"
    hp = phash(path)
    if hp is not None:
        for prev in seen_hashes:
            if hamming(hp, prev) <= PHASH_HAMMING_MAX:
                return "pHash 重复"
        seen_hashes.append(hp)
    return None


# ============================================================
# 下载 + 裁剪（20% 去水印）
# ============================================================
def _build_opener():
    proxy = os.environ.get("WERSS_PROXY", "http://127.0.0.1:7890")
    proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
    return urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=_ctx))


_opener = _build_opener()


def _download_direct(url: str, timeout: int = 20) -> bytes:
    """直接走微信原 URL 下载（不走 wemprss 代理，因为代理已挂）。"""
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://mp.weixin.qq.com/',
    })
    resp = _opener.open(req, timeout=timeout)
    return resp.read()


def _download_proxy(url: str, timeout: int = 30) -> bytes:
    """走 wemprss 图片代理下载（如果代理可用）。"""
    proxy_url = f"{WEMPRSS_BASE}/api/v1/wx/image-proxy?url=" + urllib.parse.quote(url, safe='')
    req = urllib.request.Request(proxy_url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def download_and_crop(url: str, dst: Path, crop_bottom: float = CROP_BOTTOM) -> tuple[bool, str]:
    """
    下载图片到 dst，自动裁剪下方 crop_bottom（默认 20%）去水印。
    自动 fallback：先试 wemprss 代理，失败则直接走原 URL。
    返回 (success, reason)。
    """
    dst.parent.mkdir(parents=True, exist_ok=True)

    raw_bytes = None
    used = "none"

    # 先试 wemprss 代理
    try:
        raw_bytes = _download_proxy(url)
        if raw_bytes and len(raw_bytes) > 500:
            used = "wemprss_proxy"
    except Exception:
        pass

    # Fallback：直接走微信原 URL
    if raw_bytes is None or len(raw_bytes) < 500:
        try:
            raw_bytes = _download_direct(url)
            used = "direct"
        except Exception as e:
            return False, f"下载失败: {e}"

    # 裁剪
    if crop_bottom <= 0:
        dst.write_bytes(raw_bytes)
        return True, f"ok ({used}, {len(raw_bytes)}B, no crop)"

    try:
        im = Image.open(io.BytesIO(raw_bytes))
        w, h = im.size
        if h < 50:  # 高度太小，裁 20% 也没意义
            dst.write_bytes(raw_bytes)
            return True, f"ok ({used}, {len(raw_bytes)}B, too small to crop)"
        crop_h = int(h * crop_bottom)
        cropped = im.crop((0, 0, w, h - crop_h))
        if cropped.mode in ("RGBA", "P", "LA"):
            cropped = cropped.convert("RGB")
        cropped.save(dst, "JPEG", quality=92, optimize=True)
        return True, f"ok ({used}, {w}x{h}→{cropped.size[1]}h, cropped {crop_h}px)"
    except Exception as e:
        # PIL 失败时保存原图
        dst.write_bytes(raw_bytes)
        return True, f"ok ({used}, {len(raw_bytes)}B, crop failed: {e})"


# ============================================================
# 工具函数
# ============================================================
def parse_image_urls_from_html(html_content: str) -> list:
    """从 content_html 里解析所有 <img>，返回 [{url, alt, width, height}, ...]
    自动过滤：推广上下文关键词附近的图片排除（_promo=True）。"""
    if not html_content:
        return []
    import html as html_lib
    images = []
    for m in re.finditer(r'<img[^>]+src="([^"]+)"([^>]*)>', html_content):
        url = html_lib.unescape(m.group(1))
        attrs = m.group(2)
        alt_m = re.search(r'alt="([^"]*)"', attrs)
        w_m = re.search(r'width="(\d+)"', attrs)
        h_m = re.search(r'height="(\d+)"', attrs)
        # 上下文推广检测：取图片前后200字符
        pos = m.start()
        ctx_start = max(0, pos - 200)
        ctx_end = min(len(html_content), m.end() + 200)
        context = html_content[ctx_start:ctx_end]
        # 去HTML标签，只留文字
        context_text = re.sub(r'<[^>]+>', ' ', context)
        is_promo = any(kw in context_text for kw in PROMO_CONTEXT_KEYWORDS)
        images.append({
            "url": url,
            "alt": alt_m.group(1) if alt_m else "",
            "width": int(w_m.group(1)) if w_m else None,
            "height": int(h_m.group(1)) if h_m else None,
            "_promo": is_promo,
        })
    return images


def parse_image_urls_from_markdown(md_content: str) -> list:
    """从 Markdown 内容解析所有 ![](url)，返回 [{url, alt}, ...]
    自动检测上下文推广关键词，标记 _promo=True。"""
    if not md_content:
        return []
    images = []
    for m in re.finditer(r'!\[([^\]]*)\]\((https?://[^\s\)]+)\)', md_content):
        url = m.group(2)
        alt = m.group(1)
        # 上下文推广检测：取图片前后200字符
        pos = m.start()
        ctx_start = max(0, pos - 200)
        ctx_end = min(len(md_content), m.end() + 200)
        context = md_content[ctx_start:ctx_end]
        # 去掉其他图片链接，只留文字
        context_text = re.sub(r'!\[[^\]]*\]\([^\)]+\)', '', context)
        is_promo = any(kw in context_text for kw in PROMO_CONTEXT_KEYWORDS)
        images.append({
            "url": url,
            "alt": alt,
            "width": None,
            "height": None,
            "_promo": is_promo,
        })
    return images


def unwrap_wemprss(raw: dict) -> dict:
    """解包 WeRSS 响应 {code, message, data: {...}}"""
    if isinstance(raw, dict) and 'data' in raw and isinstance(raw['data'], dict) and 'title' in raw['data']:
        return raw['data']
    return raw
