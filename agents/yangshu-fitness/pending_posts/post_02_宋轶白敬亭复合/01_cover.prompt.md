# 01_cover · 封面 Prompt（JSON 模板 · 策略 C:3:4 图生图 + 中文标题）

> 八卦风高饱和pop-art封面

```json
{
  "version": "2.0",
  "method": "image_to_image",
  "aspect_ratio": "3:4",
  "reference_image": "reference.jpg",
  "negative_prompt": "blurry, distorted Chinese, wrong text, English text, watermark, peaceful, calm, soft pastel",
  "style": {
    "background": "extracted from reference, 40% blur, neon pop-art treatment, high contrast",
    "mood": "explosive celebrity gossip clickbait, sensational, dramatic, shocking reveal, NOT calm/lifestyle",
    "color_grade": "high saturation, magenta + cyan + yellow clash, dramatic high contrast, pop-art aesthetic",
    "lighting": "harsh top-light + neon side-glow, dramatic contrast, almost cinematic noir"
  },
  "text": {
    "title": {
      "content": "宋轶白敬亭复合?",
      "position": "top-center, on neon yellow card with black border",
      "size": "extra-large, occupies top 35%",
      "color": "bold black on neon yellow (#FFE600) card",
      "font_style": "Chinese bold impact 黑体 with thick stroke, tabloid style",
      "max_chars": 18
    },
    "subtitle": {
      "content": "机场露肚子反击",
      "position": "below title",
      "size": "medium",
      "color": "white on black with red border",
      "font_style": "Chinese bold sans-serif"
    },
    "price_tag": {
      "content": "羊扒一扒",
      "position": "bottom-right, badge",
      "size": "large",
      "color": "yellow text on red (#E50914) starburst badge, 3D pop",
      "font_style": "Chinese bold display, comic book style",
      "shape": "star/sunburst"
    }
  },
  "composition": {
    "product_image": "use reference image as central element, occupying middle 50%, no soft vignette, sharp contrast",
    "decorative_elements": "exclamation marks, lightning bolt icons, speech bubble elements in corners, pop-art halftone dots overlay"
  },
  "post_generation_check": {
    "verify_chinese_text": "if Chinese text is distorted, regenerate; max 3 retries",
    "retry_strategy": "on failure, simplify text content, then try again; max 3 retries before abandoning"
  }
}
```
