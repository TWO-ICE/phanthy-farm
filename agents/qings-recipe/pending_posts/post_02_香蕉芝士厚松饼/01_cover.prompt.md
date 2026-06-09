# 01_cover · 烘焙甜品风封面（3:4 文生图 + 中文标题）

```json
{
  "version": "2.0",
  "method": "text_to_image",
  "aspect_ratio": "3:4",
  "negative_prompt": "blurry, distorted Chinese, wrong text, English text, watermark, dark, industrial, tech",
  "style": {
    "background": "soft cream beige gradient, warm bakery aesthetic",
    "mood": "warm bakery, sweet dessert, inviting food photography, cozy kitchen",
    "color_grade": "warm cream + chocolate brown + berry pink, soft pastel, appetizing",
    "lighting": "soft natural window light, golden hour warmth, food photography"
  },
  "text": {
    "title": {
      "content": "香蕉芝士厚松饼",
      "position": "top-center, on cream card",
      "size": "extra-large, top 30%",
      "color": "chocolate brown on cream",
      "font_style": "Chinese round 圆体, warm and sweet",
      "max_chars": 16
    },
    "subtitle": {
      "content": "隔夜冷藏发酵",
      "position": "below title",
      "size": "medium",
      "color": "warm grey on cream",
      "font_style": "Chinese round 圆体"
    },
    "price_tag": {
      "content": "5步搞定",
      "position": "bottom-right, badge",
      "size": "large",
      "color": "white on warm coral rounded badge",
      "font_style": "Chinese bold 圆体"
    }
  },
  "composition": {
    "product_image": "baked dessert hero shot, occupying middle 50%, soft bokeh",
    "decorative_elements": "small heart/star accents, flour dusting particles, warm tone"
  },
  "post_generation_check": {
    "verify_chinese_text": "if distorted, regenerate; max 3 retries",
    "retry_strategy": "simplify text on failure"
  }
}
```
