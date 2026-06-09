# 01_cover · 食品行业资讯风封面（3:4 图生图 + 中文标题）

```json
{
  "version": "2.0",
  "method": "image_to_image",
  "aspect_ratio": "3:4",
  "reference_image": "reference.jpg",
  "negative_prompt": "blurry, distorted Chinese, wrong text, English text, watermark, dark moody, scary, industrial, cartoon",
  "style": {
    "background": "extracted from reference, 40% blur, clean professional food industry feel",
    "mood": "professional food industry media, clean and modern, informative",
    "color_grade": "fresh green + white + soft grey, clean and professional, food industry standard",
    "lighting": "soft even light, clean studio look, bright and airy"
  },
  "text": {
    "title": {
      "content": "12款新品盘点",
      "position": "top-center, on white card with rounded corners",
      "size": "extra-large, top 25%",
      "color": "dark forest green (#1B4332) on white card",
      "font_style": "Chinese modern sans-serif, professional and clean",
      "max_chars": 18
    },
    "subtitle": {
      "content": "初夏食品圈有多卷",
      "position": "below title",
      "size": "medium",
      "color": "soft grey on white card",
      "font_style": "Chinese regular sans-serif"
    },
    "price_tag": {
      "content": "行业速览",
      "position": "bottom-right, badge",
      "size": "large",
      "color": "white text on fresh green (#2D6A4F) rounded rectangle badge",
      "font_style": "Chinese bold sans-serif"
    }
  },
  "composition": {
    "product_image": "use reference image as central element, occupying middle 50%",
    "decorative_elements": "minimal food icon accents, clean geometric shapes, green accent lines"
  },
  "post_generation_check": {
    "verify_chinese_text": "if Chinese text is distorted, regenerate; max 3 retries",
    "retry_strategy": "on failure, simplify text; max 3 retries"
  }
}
```
