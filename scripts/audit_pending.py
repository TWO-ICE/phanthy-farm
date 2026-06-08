#!/usr/bin/env python3
"""
审计 pending_posts/post_XX/ 的素材完整性。

支持方案 X（cover 是 prompt 文件 + 3 张正文图）和旧方案（4 张 png）。

用法:
  python3 audit_pending.py --agent-slug xiaoyu-tech
  python3 audit_pending.py --agent-slug xiaoyu-tech --require-cdn   # 也校验 cdn_url
"""
import argparse, json, os, sys
from pathlib import Path

FARM_ROOT = Path(os.path.expanduser("~/phanthy-farm"))
MIN_CONTENT_CHARS = 1500

def audit(post_dir: Path, require_cdn: bool) -> dict:
    result = {"post": post_dir.name, "ok": True, "missing": [], "errors": [], "warnings": []}

    mf_path = post_dir / "manifest.json"
    if not mf_path.exists():
        result["missing"].append("manifest.json")
        result["ok"] = False
        return result

    try:
        manifest = json.loads(mf_path.read_text())
    except Exception as e:
        result["errors"].append(f"manifest.json 解析失败: {e}")
        result["ok"] = False
        return result

    # 1. 文件存在性审计：以 manifest.audit.required_files 为准
    required_files = manifest.get("audit", {}).get("required_files")
    if not required_files:
        # 回退旧规则
        required_files = ["content.md", "01_cover.png", "02_original.png",
                          "03_scene.png", "04_quote.png"]
    required_files = list(required_files) + ["manifest.json"]
    for f in required_files:
        if not (post_dir / f).exists():
            result["missing"].append(f)
            result["ok"] = False

    # 2. content.md 字数 + 溯源
    content_md = post_dir / manifest.get("content_md", "content.md")
    if content_md.exists():
        text = content_md.read_text()
        plain = text
        for ch in "#*>\n\t -|":
            plain = plain.replace(ch, "")
        if len(plain) < MIN_CONTENT_CHARS:
            result["errors"].append(f"字数不足: {len(plain)} < {MIN_CONTENT_CHARS}")
            result["ok"] = False
        if "深度启发自" not in text:
            result["errors"].append("缺少原文溯源链接")
            result["ok"] = False
        # 标记词校验（改为 warning，不阻塞）
        # 新规范（v2）：用 "3 步洗稿法" 自由扩写，不强制 4 层标记词
        markers_found = []
        for marker in ["**观点：**", "**数据支撑：**", "**真实案例：**", "**落地启示：**"]:
            if marker not in text:
                markers_found.append(False)
        # 如果完全没找到任何标记词，给个温和 warning（不是必须结构）
        if not any(m in text for m in ["**观点：**", "**数据支撑：**", "**真实案例：**", "**落地启示：**"]):
            result["warnings"].append("未使用 4 层模板（v2 新规范：自由扩写即可）")

    # 3. CDN 校验（可选，发帖前由 OpenClaw 再做一遍）
    for img in manifest.get("images", []):
        # ai_prompt 类型在 OpenClaw 上传阶段才生成 png 并上传，本阶段不要求 cdn_url
        if img.get("kind") == "ai_prompt":
            continue
        if require_cdn and not img.get("cdn_url"):
            result["errors"].append(f"图片未上传 CDN: {img.get('slot')}")
            result["ok"] = False

    # 4. 封面 prompt 文件校验（ai_prompt 类型必须配 prompt_file）
    for img in manifest.get("images", []):
        if img.get("kind") == "ai_prompt":
            pf = img.get("prompt_file")
            if not pf:
                result["errors"].append("ai_prompt 图缺 prompt_file 字段")
                result["ok"] = False
            elif not (post_dir / pf).exists():
                result["missing"].append(pf)
                result["ok"] = False

    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent-slug", required=True)
    ap.add_argument("--require-cdn", action="store_true",
                    help="也校验图片是否已上传 CDN（默认不校验）")
    args = ap.parse_args()

    pending = FARM_ROOT / "agents" / args.agent_slug / "pending_posts"
    if not pending.exists():
        print(json.dumps({"error": f"{pending} 不存在"}, ensure_ascii=False))
        sys.exit(1)

    results = []
    for d in sorted(pending.iterdir()):
        if d.is_dir():
            results.append(audit(d, args.require_cdn))

    print(json.dumps({"total": len(results),
                      "ok": sum(1 for r in results if r["ok"]),
                      "results": results}, ensure_ascii=False, indent=2))
    sys.exit(0 if all(r["ok"] for r in results) else 1)

if __name__ == "__main__":
    main()
