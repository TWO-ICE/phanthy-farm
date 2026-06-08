# 01_cover · 封面 Prompt（JSON 模板 · 策略 C:3:4 图生图 + 中文标题）

> 本文件是 **JSON 结构化模板**，agent 读取后填入占位符 → 调 gemini-image。
> **method**: 图生图，参考图 = `reference.jpg`
> **aspect_ratio**: 3:4 竖版（适配 phanthy 移动端 feed 卡片）
> **占位符**: `{TITLE}` / `{SUBTITLE}` / `{PRICE}` 已预填

```json
{
  "version": "2.0",
  "method": "image_to_image",
  "aspect_ratio": "3:4",
  "reference_image": "reference.jpg",
  "negative_prompt": "blurry, distorted Chinese characters, wrong text, English text, watermark, logo, busy decoration, frame border, neon colors, plastic texture",
  "style": {
    "background": "extracted and softly blurred from reference image, 50% blur, clean cream/ivory tone",
    "mood": "warm, healing, slow-life handcraft aesthetic, cozy craft workshop vibe, NOT urgent or clickbait",
    "color_grade": "cream white + oatmeal + light wood, low saturation, film grain texture, warm soft tone",
    "lighting": "soft top-left natural window light, golden hour feel, gentle product hero shot"
  },
  "text": {
    "title": {
      "content": "漫汐钩针裙边包",
      "position": "top-center, on cream/ivory card with subtle wood-grain shadow",
      "size": "extra-large, occupies top 28%",
      "color": "warm dark brown (#5C3A21) on cream white card",
      "font_style": "modern Chinese 楷体/思源宋体风, elegant and soft, NOT bold impact",
      "max_chars": 18
    },
    "subtitle": {
      "content": "法式慵懒 随手拿捏",
      "position": "below title, smaller card",
      "size": "medium",
      "color": "warm grey on cream",
      "font_style": "Chinese regular 楷体, soft handwritten feel"
    },
    "price_tag": {
      "content": "新品85折",
      "position": "bottom-right, prominent badge",
      "size": "large",
      "color": "warm brown text on cream beige (#F5E6D3) circular or rectangular badge with thin brown border",
      "font_style": "Chinese 楷体, NO 3D shadow, flat vintage feel",
      "shape": "rectangle with rounded corners (NOT circle/star)"
    }
  },
  "composition": {
    "product_image": "use reference image as central element, occupying middle 50%, soft vignette",
    "decorative_elements": "subtle linen/canvas texture overlay on edges (top-left + bottom-right), no watermarks, no icons"
  },
  "post_generation_check": {
    "verify_chinese_text": "if Chinese text is distorted, regenerate with simpler text; max 3 retries",
    "retry_strategy": "on failure, simplify text content, then try again; max 3 retries before abandoning"
  }
}
```
