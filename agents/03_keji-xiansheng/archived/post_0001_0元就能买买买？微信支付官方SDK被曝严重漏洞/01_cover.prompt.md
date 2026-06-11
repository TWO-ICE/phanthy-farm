{
  "version": "3.0",
  "model": "gemini-image",
  "visual_system": "swiss",
  "palette": "ikb-blue",
  "layout_recipe": "C09",
  "aspect_ratio": "3:4",
  "reference_image": "reference.jpg",
  "style_prompt": "Swiss International style cover, strict left-aligned grid layout, clean and engineered. Bright off-white paper background (#fafaf8). Large bold statement title with light weight (NOT heavy thick). One IKB Blue (#002FA7) accent block or bar. Hairline horizontal rules. No gradients, no shadows, no glass effects, no decorative elements. Flat even lighting. Data-driven and decisive mood, like a high-end tech conference keynote slide.",
  "negative_prompt": "blurry, distorted Chinese characters, wrong text, English text instead of Chinese, watermark, logo, busy decoration, frame border, low quality, pixelated, nested cards, rounded SaaS card layouts, random decorative SVG blobs, heavy bold oversized titles (weight 700+), gradients, shadows, glass morphism, colorful background, multiple accent colors, illustration, cartoon, photo of people, hand-drawn elements",
  "title": {
    "content": "0元就能买买买微信支付官方SDK被曝严重",
    "max_chars": 20,
    "font_style": "Chinese sans-serif (黑体/Inter), weight 300-400, the bigger the lighter",
    "color": "pure black (#0a0a0a) on off-white background, maximum contrast",
    "position": "left-aligned, occupies top 40-50% of canvas, 2-3 lines maximum"
  },
  "subtitle": {
    "content": "科技先生科技主题的极客新闻和社区，有趣，有料！\n\n\n\n\n———— / ",
    "max_chars": 35,
    "font_style": "mono (等宽字体), small, uppercase tracking",
    "color": "medium grey (#737373)"
  },
  "composition": "Statement cover layout. Large light-weight title left-aligned in top 50%. One IKB Blue (#002FA7) horizontal accent bar at top or between title and subtitle. Small mono metadata line at bottom with date and category tag. Clean hairline rules separating sections. If reference image exists: place it as a small framed rectangle in the bottom-right 30% with thin border, NOT full-bleed. If no reference image: text-only, pure Swiss grid, no illustration substitute.",
  "fallback": {
    "no_reference": "text-only Swiss grid layout with IKB Blue accent bar, no placeholder images",
    "text_distorted": "simplify title to 10 chars max and retry",
    "max_retries": 3,
    "final_fallback": "crop reference.jpg to 3:4 as cover"
  }
}