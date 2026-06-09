# 01_cover · 封面 Prompt（JSON 模板 · 策略 C:3:4 图生图 + 中文标题）

> 本文件是 **JSON 结构化模板**，agent 读取后填入占位符 → 调 gemini-image。
> **method**: 图生图，参考图 = `reference.jpg`
> **aspect_ratio**: 3:4 竖版（适配 phanthy 移动端 feed 卡片）

```json
{
  "version": "2.0",
  "method": "image_to_image",
  "aspect_ratio": "3:4",
  "reference_image": "reference.jpg",
  "negative_prompt": "blurry, distorted Chinese characters, wrong text, English text, watermark, logo, busy decoration, frame border, neon colors, harsh contrast, stock photo",
  "style": {
    "background": "extracted and softly blurred from reference image, 60% blur, warm cream/ivory tone with gentle gradient",
    "mood": "warm, healing, poetic, gentle emotional essay aesthetic, like a handwritten letter, NOT clickbait or urgent",
    "color_grade": "cream white + soft peach + warm grey, low saturation, matte paper texture, film grain",
    "lighting": "soft diffused light from top, warm golden hour feel, like afternoon light through curtains"
  },
  "text": {
    "title": {
      "content": "1%幸福效应",
      "position": "center, on cream/ivory card with subtle shadow",
      "size": "large, occupies middle 30%",
      "color": "warm dark grey (#4A4040) on cream white card",
      "font_style": "modern Chinese 楷体/思源宋体风, elegant and soft, NOT bold impact",
      "max_chars": 18
    },
    "subtitle": {
      "content": "明媚开朗的小秘诀",
      "position": "below title, smaller",
      "size": "medium",
      "color": "warm grey on cream",
      "font_style": "Chinese regular 楷体, soft handwritten feel"
    },
    "tag": {
      "content": "自我成长",
      "position": "top-left, small label",
      "size": "small",
      "color": "soft peach text on cream badge",
      "font_style": "Chinese regular, minimal",
      "shape": "rounded rectangle with thin warm grey border"
    }
  },
  "composition": {
    "product_image": "use reference image mood as base, soft gradient overlay, gentle vignette",
    "decorative_elements": "subtle paper texture overlay on edges, tiny dot or leaf accent, no watermarks, no icons"
  },
  "post_generation_check": {
    "verify_chinese_text": "if Chinese text is distorted, regenerate with simpler text; max 3 retries",
    "retry_strategy": "on failure, simplify text content, then try again; max 3 retries before abandoning"
  }
}
```