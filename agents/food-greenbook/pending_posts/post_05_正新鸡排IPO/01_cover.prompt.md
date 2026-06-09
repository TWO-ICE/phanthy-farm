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
    "mood": "professional food industry media, clean and modern, investigative journalism tone",
    "color_grade": "red-orange + dark grey + white, bold brand analysis feel",
    "lighting": "soft even light, clean studio look, professional"
  },
  "text": {
    "title": {
      "content": "正新鸡排IPO",
      "position": "top-center, on white card with rounded corners",
      "size": "extra-large, top 25%",
      "color": "dark charcoal (#1C1917) on white card",
      "font_style": "Chinese modern sans-serif, professional and clean",
      "max_chars": 18
    },
    "subtitle": {
      "content": "万店帝国的起落",
      "position": "below title",
      "size": "medium",
      "color": "soft grey on white card",
      "font_style": "Chinese regular sans-serif"
    },
    "price_tag": {
      "content": "品牌拆解",
      "position": "bottom-right, badge",
      "size": "large",
      "color": "white text on red-orange (#C2410C) rounded rectangle badge",
      "font_style": "Chinese bold sans-serif"
    }
  },
  "composition": {
    "product_image": "use reference image as central element, occupying middle 50%",
    "decorative_elements": "minimal chart icon accents, clean geometric shapes, red accent lines"
  },
  "post_generation_check": {
    "verify_chinese_text": "if Chinese text is distorted, regenerate; max 3 retries",
    "retry_strategy": "on failure, simplify text; max 3 retries"
  }
}
```
