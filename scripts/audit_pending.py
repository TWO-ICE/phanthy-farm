#!/usr/bin/env python3
"""
审计 pending_posts/post_XX/ 的素材完整性。

【v3 规范】"完" 状态机：
  - 文件夹名以 "完" 结尾 → 已完成 (state=done)，严格审计 4 必含 + 至少 1 张图
  - 文件夹名不以 "完" 结尾 → 未完成 (state=pending)，只回报进度，不算失败

必含文件（v3 新规范，不再要求固定 6 文件）：
  1. content.md
  2. manifest.json
  3. 01_cover.prompt.md
  4. reference.jpg (原文封面)

正文图（v3 新规范：充分下载，不再限 3 张）：
  - 至少 1 张 img_*.jpg（充分下载后筛过的）
  - 推荐 5+ 张，多多益善

用法:
  python3 audit_pending.py --agent-slug xiaoyu-tech
  python3 audit_pending.py --agent-slug xiaoyu-tech --require-cdn   # 也校验 cdn_url
"""
import argparse, json, os, re, sys
from pathlib import Path

# 真实仓库路径（v3 修正：之前指向 ~/phanthy-farm 是 stale 副本）
FARM_ROOT_CANDIDATES = [
    Path(os.environ.get("PHANTHY_REPO", "/Users/4paradigm/Documents/phanthy")),
    Path(os.path.expanduser("~/phanthy-farm")),  # 兼容旧路径
]
FARM_ROOT = next((p for p in FARM_ROOT_CANDIDATES if p.exists()), FARM_ROOT_CANDIDATES[0])

MIN_CONTENT_CHARS = 1500
MIN_BODY_IMAGES = 1  # 至少 1 张正文图（推荐 5+）


def _plain_chars(text: str) -> int:
    """去格式符号后的纯字符数"""
    plain = text
    for ch in "#*>\n\t -|":
        plain = plain.replace(ch, "")
    return len(plain)


def audit(post_dir: Path, require_cdn: bool) -> dict:
    is_done = post_dir.name.endswith("完")
    result = {
        "post": post_dir.name,
        "state": "done" if is_done else "pending",
        "ok": is_done,  # 初始值：done=按审计结果，pending=默认 ok（不算失败）
        "missing": [],
        "errors": [],
        "warnings": [],
        "stats": {},
    }

    md_path = post_dir / "content.md"

    # ===== 非"完" 状态：只回报进度 =====
    if not is_done:
        has_content = md_path.exists()
        has_imgs = any(post_dir.glob("img_*.jpg"))
        has_manifest = (post_dir / "manifest.json").exists()

        if has_content and not has_manifest and not has_imgs:
            # 有 content.md 但没图没 manifest → "缺图" 状态（LLM 写过但图过滤太严）
            result["state"] = "missing_images"
            text = md_path.read_text(encoding='utf-8')
            chars = _plain_chars(text)
            result["stats"]["chars"] = chars
            result["stats"]["imgs"] = 0
            missing_note = (post_dir / "MISSING_IMGS")
            if missing_note.exists():
                result["warnings"].append(f"缺图（{chars} 字已写，MISSING_IMGS 标记存在）")
            else:
                result["warnings"].append(f"缺图（{chars} 字已写，待重跑图过滤）")
        elif has_content:
            text = md_path.read_text(encoding='utf-8')
            chars = _plain_chars(text)
            result["stats"]["chars"] = chars
            result["stats"]["imgs"] = len(list(post_dir.glob("img_*.jpg")))
            result["warnings"].append(f"未完，当前 {chars} 字 / {result['stats']['imgs']} 图")
        else:
            result["warnings"].append("未完，缺 content.md")
        return result

    # ===== "完" 状态：严格审计 =====
    # 1. 4 必含文件
    required = ["content.md", "manifest.json", "01_cover.prompt.md", "reference.jpg"]
    for f in required:
        if not (post_dir / f).exists():
            result["missing"].append(f)
            result["ok"] = False

    # 2. 正文图（v3 充分下载）
    imgs = sorted(post_dir.glob("img_*.jpg"))
    if not imgs:
        result["errors"].append(f"缺正文图（至少 {MIN_BODY_IMAGES} 张）")
        result["ok"] = False
    elif len(imgs) < 3:
        result["warnings"].append(f"正文图 {len(imgs)} 张 < 3，推荐 5+")
    result["stats"]["body_images"] = len(imgs)

    # 3. manifest.json 解析 + CDN 校验
    mf_path = post_dir / "manifest.json"
    if mf_path.exists():
        try:
            manifest = json.loads(mf_path.read_text(encoding='utf-8'))
        except Exception as e:
            result["errors"].append(f"manifest.json 解析失败: {e}")
            result["ok"] = False
            manifest = {}

        # ai_prompt 类型图必须配 prompt_file
        for img in manifest.get("images", []):
            if img.get("kind") == "ai_prompt":
                pf = img.get("prompt_file")
                if not pf:
                    result["errors"].append("ai_prompt 图缺 prompt_file 字段")
                    result["ok"] = False
                elif not (post_dir / pf).exists():
                    result["missing"].append(pf)
                    result["ok"] = False

        # CDN 校验（可选）
        if require_cdn:
            for img in manifest.get("images", []):
                if img.get("kind") == "ai_prompt":
                    continue
                if not img.get("cdn_url"):
                    result["errors"].append(f"图片未上传 CDN: {img.get('slot')}")
                    result["ok"] = False

    # 4. content.md 字数 + 溯源
    if md_path.exists():
        text = md_path.read_text(encoding='utf-8')
        chars = _plain_chars(text)
        if chars < MIN_CONTENT_CHARS:
            result["errors"].append(f"字数不足: {chars} < {MIN_CONTENT_CHARS}")
            result["ok"] = False
        if "深度启发自" not in text:
            result["errors"].append("缺少原文溯源链接（'深度启发自'）")
            result["ok"] = False
        result["stats"]["chars"] = chars

    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent-slug", required=True)
    ap.add_argument("--require-cdn", action="store_true",
                    help="也校验图片是否已上传 CDN（默认不校验）")
    args = ap.parse_args()

    pending = FARM_ROOT / "agents" / args.agent_slug / "pending_posts"
    if not pending.exists():
        print(json.dumps({"error": f"{pending} 不存在", "farm_root": str(FARM_ROOT)},
                         ensure_ascii=False))
        sys.exit(1)

    # 数字序排序（按 post_XX 中的 XX 排）
    def numeric_key(name):
        m = re.match(r'^post_(\d+)_', name)
        return int(m.group(1)) if m else 0

    results = []
    for d in sorted(pending.iterdir(), key=lambda x: (numeric_key(x.name), x.name)):
        if d.is_dir():
            results.append(audit(d, args.require_cdn))

    # 分类统计
    done = [r for r in results if r["state"] == "done"]
    pending = [r for r in results if r["state"] == "pending"]
    done_ok = sum(1 for r in done if r["ok"])
    pending_with_md = sum(1 for r in pending if (Path(r["post"]) / "content.md").exists()
                          or any("未完，当前" in w for w in r.get("warnings", [])))

    summary = {
        "total": len(results),
        "done": len(done),
        "done_ok": done_ok,
        "done_failed": len(done) - done_ok,
        "pending": len(pending),
        "pending_with_md": pending_with_md,
        "farm_root": str(FARM_ROOT),
        "agent_slug": args.agent_slug,
        "results": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    # 退出码：只有 done_failed 才失败，pending 不算
    if done_ok < len(done):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
