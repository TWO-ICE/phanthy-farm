#!/usr/bin/env python3
"""
根据 manifest + 模板，生成 01_cover.prompt.md (JSON 格式)。
统一风格：3:4 竖版、图生图、中文标题、价格标签。

用法:
  python3 build_cover_prompt.py <post_dir>
"""
import json, os, sys
from pathlib import Path

TEMPLATE = {
  "version": "2.0",
  "method": "image_to_image",
  "aspect_ratio": "3:4",
  "reference_image": "reference.jpg",
  "negative_prompt": "blurry, distorted Chinese characters, wrong text, English text instead of Chinese, watermark, logo, busy decoration, frame border",
  "style": {
    "background": "extracted and softly blurred from reference image, 40% blur for clean text overlay area",
    "mood": "exciting second-hand deal discovery, urgent and clickable, Xianyu marketplace vibe",
    "color_grade": "warm beige + cool steel grey, slightly desaturated, kraft paper texture overlay on edges",
    "lighting": "soft top-left directional light, product hero shot feel"
  },
  "text": {
    "title": {
      "content": "{{TITLE}}",
      "position": "top-center, on white card with subtle shadow",
      "size": "extra-large, occupies top 30%",
      "color": "bold black text on clean white card background",
      "font_style": "modern Chinese bold sans-serif (黑体/思源黑体风), high impact",
      "max_chars": 22
    },
    "subtitle": {
      "content": "{{SUBTITLE}}",
      "position": "below title, smaller card",
      "size": "medium",
      "color": "dark grey on white",
      "font_style": "Chinese regular sans-serif"
    },
    "price_tag": {
      "content": "{{PRICE}}",
      "position": "bottom-right, prominent badge",
      "size": "extra-large, star element",
      "color": "white text on bright red/orange (#FF4500) circular or star-shaped badge with thick white border",
      "font_style": "Chinese bold display font, slight 3D shadow effect"
    }
  },
  "composition": {
    "product_image": "use reference image as central element, occupying middle 50%",
    "decorative_elements": "small subtle Xianyu/二手鱼 fish icon watermark (top-right corner, low opacity), price tag string detail"
  },
  "post_generation_check": {
    "verify_chinese_text": "if Chinese text is distorted or wrong characters, regenerate with simpler text",
    "retry_strategy": "on failure, simplify text content, then try again; max 3 retries before abandoning"
  }
}


def build(post_dir: Path):
    post_dir = Path(post_dir)
    manifest_path = post_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"❌ {manifest_path} 不存在")
        sys.exit(1)

    manifest = json.loads(manifest_path.read_text())
    title = manifest["title"]
    # 从 title 拆分主标题 + 副标题（按"？"或","分）
    # 优先用 manifest.cover_text 字段（如果提供）
    cover_text = manifest.get("cover_text")
    if cover_text:
        main_title = cover_text.get("title", title)
        subtitle = cover_text.get("subtitle", "")
        price = cover_text.get("price", "")
    else:
        # 默认拆分
        main_title = title
        subtitle = ""
        price = ""

    data = json.loads(json.dumps(TEMPLATE))  # deep copy
    data["text"]["title"]["content"] = main_title
    data["text"]["subtitle"]["content"] = subtitle
    data["text"]["price_tag"]["content"] = price

    out_path = post_dir / "01_cover.prompt.md"
    # 输出为 markdown 包裹的 JSON（方便人读 + 机器解析）
    content = (
        f"# 01_cover · 封面 Prompt（JSON 模板 · 策略 C:3:4 图生图 + 中文标题）\n\n"
        f"> 本文件是 **JSON 结构化模板**，agent 读取后填入占位符 → 调 gemini-image。\n"
        f"> **method**: 图生图，参考图 = `reference.jpg`\n"
        f"> **aspect_ratio**: 3:4 竖版（适配 phanthy 移动端 feed 卡片）\n"
        f"> **占位符**: `{{TITLE}}` / `{{SUBTITLE}}` / `{{PRICE}}` 已预填\n\n"
        f"```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```\n"
    )
    out_path.write_text(content)
    print(f"✅ {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python3 build_cover_prompt.py <post_dir>")
        sys.exit(1)
    build(sys.argv[1])
