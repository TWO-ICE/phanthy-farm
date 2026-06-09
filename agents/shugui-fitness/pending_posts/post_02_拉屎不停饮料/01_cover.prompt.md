# 01_cover · 健身科普风封面（3:4 文生图 + 中文标题）

```json
{
  "version": "2.0",
  "method": "text_to_image",
  "aspect_ratio": "3:4",
  "negative_prompt": "blurry, distorted Chinese, wrong text, English text, watermark, cute, pastel, food",
  "style": {
    "background": "dark gradient, charcoal grey to black, gym aesthetic",
    "mood": "powerful fitness motivation, strong and energetic, no-nonsense",
    "color_grade": "high contrast, bold black + electric blue/red accent, dynamic",
    "lighting": "dramatic side lighting, gym spotlight feel, strong shadows"
  },
  "text": {
    "title": {
      "content": "拉屎不停饮料",
      "position": "top-center, on dark card",
      "size": "extra-large, top 30%",
      "color": "white on dark grey card",
      "font_style": "Chinese bold 黑体, strong and impactful",
      "max_chars": 16
    },
    "subtitle": {
      "content": "叔贵亲测颁奖",
      "position": "below title",
      "size": "medium",
      "color": "light grey on dark",
      "font_style": "Chinese bold sans-serif"
    },
    "price_tag": {
      "content": "618推荐",
      "position": "bottom-right, badge",
      "size": "large",
      "color": "white on electric blue (#0066FF) rounded badge",
      "font_style": "Chinese bold"
    }
  },
  "composition": {
    "product_image": "fitness/movement imagery, occupying middle 50%",
    "decorative_elements": "subtle geometric lines, energy lines, dynamic feel"
  },
  "post_generation_check": {
    "verify_chinese_text": "if distorted, regenerate; max 3 retries",
    "retry_strategy": "simplify text on failure"
  }
}
```
