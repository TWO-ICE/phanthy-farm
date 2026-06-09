# 01_cover · 零食风封面（3:4 图生图 + 中文标题）

```json
{
  "version": "2.0",
  "method": "image_to_image",
  "aspect_ratio": "3:4",
  "reference_image": "reference.jpg",
  "negative_prompt": "blurry, distorted Chinese, wrong text, English text, watermark, dark moody, scary, industrial",
  "style": {
    "background": "extracted from reference, 40% blur, warm inviting food photography feel",
    "mood": "appetizing food blogger, warm and friendly, snack recommendation, colorful and inviting",
    "color_grade": "warm orange + soft yellow + cream white, high saturation food colors, appetizing",
    "lighting": "soft natural window light, food photography golden hour, warm and bright"
  },
  "text": {
    "title": {
      "content": "PDD零食自由",
      "position": "top-center, on white card with rounded corners",
      "size": "extra-large, top 30%",
      "color": "dark chocolate brown (#4A2C2A) on cream white card",
      "font_style": "Chinese 圆体/手写风, friendly and warm",
      "max_chars": 18
    },
    "subtitle": {
      "content": "配料表干净好吃",
      "position": "below title",
      "size": "medium",
      "color": "warm grey on cream",
      "font_style": "Chinese regular 圆体"
    },
    "price_tag": {
      "content": "6款宝藏",
      "position": "bottom-right, badge",
      "size": "large",
      "color": "white text on warm coral (#FF6B6B) rounded rectangle badge",
      "font_style": "Chinese bold 圆体"
    }
  },
  "composition": {
    "product_image": "use reference image as central element, occupying middle 50%",
    "decorative_elements": "small food icon accents (star/circle), warm tone, NO fish/tech icons"
  },
  "post_generation_check": {
    "verify_chinese_text": "if Chinese text is distorted, regenerate; max 3 retries",
    "retry_strategy": "on failure, simplify text; max 3 retries"
  }
}
```
