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
    "color_grade": "cool blue + white + soft grey, health-conscious beverage feel",
    "lighting": "soft even light, clean studio look, bright and airy"
  },
  "text": {
    "title": {
      "content": "低GI冰红茶时代",
      "position": "top-center, on white card with rounded corners",
      "size": "extra-large, top 25%",
      "color": "deep teal (#0A4D68) on white card",
      "font_style": "Chinese modern sans-serif, professional and clean",
      "max_chars": 18
    },
    "subtitle": {
      "content": "减糖不减痛快",
      "position": "below title",
      "size": "medium",
      "color": "soft grey on white card",
      "font_style": "Chinese regular sans-serif"
    },
    "price_tag": {
      "content": "行业深度",
      "position": "bottom-right, badge",
      "size": "large",
      "color": "white text on teal (#088395) rounded rectangle badge",
      "font_style": "Chinese bold sans-serif"
    }
  },
  "composition": {
    "product_image": "use reference image as central element, occupying middle 50%",
    "decorative_elements": "minimal health icon accents, clean geometric shapes, blue accent lines"
  },
  "post_generation_check": {
    "verify_chinese_text": "if Chinese text is distorted, regenerate; max 3 retries",
    "retry_strategy": "on failure, simplify text; max 3 retries"
  }
}
```
