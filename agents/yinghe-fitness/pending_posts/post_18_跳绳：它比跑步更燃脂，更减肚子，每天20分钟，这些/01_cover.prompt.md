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
  "negative_prompt": "blurry, distorted Chinese characters, wrong text, English text instead of Chinese, watermark, logo, busy decoration, frame border",
  "style": {
    "background": "extracted and softly blurred from reference image, 40% blur for clean text overlay area",
    "mood": "exciting second-hand deal discovery, urgent and clickable, Xianyu marketplace vibe",
    "color_grade": "warm beige + cool steel grey, slightly desaturated, kraft paper texture overlay on edges",
    "lighting": "soft top-left directional light, product hero shot feel"
  },
  "text": {
    "title": {
      "content": "跳绳：它比跑步更燃脂，更减肚子，每天",
      "position": "top-center, on white card with subtle shadow",
      "size": "extra-large, occupies top 30%",
      "color": "bold black text on clean white card background",
      "font_style": "modern Chinese bold sans-serif (黑体/思源黑体风), high impact",
      "max_chars": 22
    },
    "subtitle": {
      "content": "",
      "position": "below title, smaller card",
      "size": "medium",
      "color": "dark grey on white",
      "font_style": "Chinese regular sans-serif"
    },
    "price_tag": {
      "content": "",
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
```
