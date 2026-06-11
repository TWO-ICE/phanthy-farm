# TUNING.md — 音乐先声（yinyue-xiansheng）

> 本文件记录 per-agent 的精调参数：仿写策略、封面设计、正文配图。
> 与 SOUL.md（人设）和 AGENT_RULES.md（流程）配合使用。

---

## 1. 仿写策略

- 目标字数：**3500-4500字**（科技新闻类深度报道）
- 骨架：现象→数据→分析→判断→总结
- 扩容手法：补充行业数据、竞品对比、用户视角
- 纯 Markdown，无图（去 `![](url)`）
- 末尾：`> 💡 深度启发自：[标题](URL)`

### 模型配置

- 主力模型：**glm-4.7**（thinking:disabled，max_tokens=65536）
- 备选：MiniMax-M2.7（限流时）
- 标题：仿写完成后用 glm-4-flash 起新标题（≤20字），写回 content.md 第一行

---

## 2. 封面设计规则（[COVER]）

> 基于 `docs/cover-design-rules.md` v2 通用规则精调。
> 视觉体系源自 guizang-social-card-skill，翻译为 Gemini Image prompt。

### 基础参数

```ini
[COVER]
VISUAL_SYSTEM = swiss
PALETTE = ikb-blue
LAYOUT_RECIPE = C09
```

### 完整 Prompt 参数

```json
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
    "content": "{TITLE}",
    "max_chars": 20,
    "font_style": "Chinese sans-serif (黑体/Inter), weight 300-400, the bigger the lighter",
    "color": "pure black (#0a0a0a) on off-white background, maximum contrast",
    "position": "left-aligned, occupies top 40-50% of canvas, 2-3 lines maximum"
  },

  "subtitle": {
    "content": "{SUMMARY}",
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
```

### 设计决策说明

| 决策 | 理由 |
|---|---|
| Swiss 而非 Editorial | 音乐先声是**快节奏新闻速报**，需要工程冷感而非慢阅读杂志感 |
| IKB Blue | 国际克莱因蓝是科技/AI/工程领域的默认色，与华为/5G/芯片等内容天然匹配 |
| C09 声明式封面 | 科技新闻标题本身就是观点（"华为没有对手""苹果紧急回应"），适合大字声明式排版 |
| 标题 ≤20 字 | 音乐先声标题偏长（平均 18-22 字），取核心观点压缩到 20 字 |
| 大字轻量（300-400 weight） | Swiss 铁律：越大越细。大标题用细体而非粗体，避免"PPT 宣传海报"廉价感 |
| 不用图做主角 | 科技新闻配图多为产品照/截图，质量参差。以文字排版为主，参考图缩小放右下角 |
| 无图时纯排版 | 不用 AI 生成插图填充——Swiss 的力量在于排版本身 |

### 标题压缩规则

音乐先声原标题常超 20 字，喂给封面前必须压缩。规则：

1. 去掉语气词（"赶紧""重磅""没想到"）
2. 提取核心主语 + 核心动作/判断
3. 保留数据/型号（"Mate X5""骁龙855"）
4. 示例：
   - 原始：`年度最强全能旗舰！华为Mate X5没有对手` → 封面：`华为 Mate X5 没有对手`
   - 原始：`赶紧升级微信！不只有看一看，还有这些实用功能！` → 封面：`微信新功能速览`
   - 原始：`华为海思总裁邮件：所有的芯片备胎，一夜之间全部转"正"` → 封面：`芯片备胎一夜转正`

---

## 3. 正文配图规则

### 风格
- 科技插画风：简约几何+数据可视化元素
- 色调与封面一致（IKB Blue + 黑白灰）
- 每页一张，文字内容精炼提取

### 处理流程（**必须用 `_lib.py`**）
- **一级过滤**：排除二维码/名片/GIF/推广图/封面图/比例异常（w/h<0.3 或 >5）
- **下载后裁剪底部20%**：去公众号水印（`CROP_BOTTOM=0.20`）
- **二级过滤**：<8KB / 尺寸<300px / 纯色空白 / pHash去重
- 数量：每篇最多 20 张，不限下限（有几张用几张）

---

## 4. 三件套确认

每篇 post 包含：
1. `content.md` — 仿写正文（第一行 `# 标题`）
2. `cover.png` — 封面图（1080×1440，3:4）
3. `body_pages/` — 正文配图（page_001.png ~ page_020.png）
