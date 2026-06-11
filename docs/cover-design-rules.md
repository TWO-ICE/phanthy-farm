# 通用封面图生成规则 v2

> 适用于 Phanthy Farm 所有 agent。视觉体系源自 guizang-social-card-skill，翻译为 Gemini Image prompt 语言。
> 线上龙虾读取 `01_cover.prompt.md` → 调 Gemini Image API → 输出封面图。

---

## 一、两套视觉系统

所有 agent 封面必须从以下两套系统中**选一套**，不混用、不自创。

### 系统 A：Editorial Magazine × E-ink

**视觉内核**：宋体/衬线 + 墨水纸质感 + 杂志排版节奏（ledger / marginalia / pull-quote / photo-well）。

**适用**：慢阅读感、专栏叙事、人文类、生活类、长文深度内容。读起来像翻开一本被偏爱的杂志。

**prompt 关键词**：
```
style: "Editorial magazine cover, premium print quality"
background: "warm paper texture with subtle ink grain, NOT flat solid color"
font: "Chinese serif typeface (宋体/思源宋体), elegant and refined"
mood: "slow, considered, hand-set, like a literary magazine feature"
lighting: "soft natural diffused light, warm paper tone"
```

**6 套官方调色板**（不可自定义，只选其一）：

| 名称 | prompt 描述 | 适用内容 |
|---|---|---|
| Ink Classic | `warm ivory paper (#f3f0e8), deep ink black (#0a0a0b), muted brown accents` | 商业评论、产品思考、中性社论 |
| Indigo Porcelain | `cool blue-grey paper (#f2f4f5), deep navy ink (#0a1f3d), steel blue accent (#315d93)` | 科技、数据、AI、研究分析 |
| Forest Ink | `warm natural paper (#f5f1e8), deep forest ink (#16251b), sage green accent (#2e6b4f)` | 户外、自然、可持续、田野笔记 |
| Kraft Paper | `warm kraft (#eedfc7), dark brown ink (#2a1e13), burnt sienna accent (#9b5a2e)` | 记忆、手作、旧物、创作者笔记 |
| Dune | `warm sand (#f0e6d2), dark umber ink (#1f1a14), muted gold accent (#8f7650)` | 设计、器物、画廊感、克制美学 |
| Midnight Ink | `deep charcoal black (#0e0d0c), warm cream ink (#ece2cf), gilt amber accent (#d4a04a), only official dark editorial palette` | 游戏封面、夜景摄影、暗调电影感 |

### 系统 B：Swiss International

**视觉内核**：Inter/黑体无衬线 + 单一 accent 色 + 严格左对齐网格 + 数据矩阵感。

**适用**：工程感、数据感、快节奏、新闻速报、产品发布。读起来像一份精密的工程蓝图。

**prompt 关键词**：
```
style: "Swiss International style, strict grid layout, clean and engineered"
background: "bright white/off-white (#fafaf8), minimal and clean"
font: "Chinese bold sans-serif (黑体/思源黑体/Inter), light weight at large sizes"
mood: "decisive, quantified, systematic, data-driven"
lighting: "flat even lighting, no dramatic shadows"
```

**4 套官方调色板**（不可自定义，只选其一）：

| 名称 | Accent 色 | prompt 描述 | 适用内容 |
|---|---|---|---|
| IKB Blue | `#002FA7` | `bright white base, pure International Klein Blue (#002FA7) accent` | 科技、AI、产品更新、工程（默认推荐） |
| Lemon Yellow | `#FFD500` | `bright white base, bold lemon yellow (#FFD500) accent, dark text on yellow` | 年轻消费、零售、运动、活泼 |
| Lemon Green | `#C5E803` | `bright white base, highlighter green (#C5E803) accent, dark text on green` | 生态、未来科技、健康、新兴趋势 |
| Safety Orange | `#FF6B35` | `bright white base, safety orange (#FF6B35) accent, white text on orange` | 工业、警告、紧迫、风险、决策 |

---

## 二、封面布局食谱（10 种）

每种食谱对应一种页面结构，agent 精调时选择其一。

### C01 — 杂志封面（Magazine Issue Cover）

**系统**：Editorial
**结构**：顶部类别条 + 大标题 2-4 行 + 一张占 35%-55% 的大图 + 底部 issue strip（3-5 要点）

```
composition: {
  top_band: "category label with date, small mono font",
  title_area: "large serif title, 2-4 lines, occupies top 35%",
  image_area: "large rectangular photo well, 35-55% of canvas, can bleed edges",
  bottom_strip: "3-5 short bullet points in small mono font, separated by em-dash"
}
```

### C02 — 实地记录（Field Note Photo）

**系统**：Editorial
**结构**：一张纪实大图 + 窄说明栏 + 一句核心观点大字

```
composition: {
  image_area: "large documentary photo, 55-65% of canvas",
  caption: "narrow caption column or bottom band, small sans-serif",
  takeaway: "one short takeaway in large serif type, positioned to not overlap photo subject"
}
```

### C03 — 社论对分（Editorial Essay Split）

**系统**：Editorial
**结构**：左列大标题/引言 + 右列 2-3 短段 + 细线分隔

```
composition: {
  left_column: "large title or pull quote, 45% width",
  right_column: "2-3 short paragraphs, 50% width",
  divider: "thin vertical hairline rule between columns",
  gap: "clean separation, no decorative elements"
}
```

### C04 — 核心论点（Pull Quote / Thesis）

**系统**：Editorial
**结构**：一条贯穿页面的巨大引言 + 小出处行 + 底部元数据条

```
composition: {
  quote: "one very large serif quote, centered, 2-3 lines, occupies 50-60% of canvas",
  source: "small attribution line below quote, mono font",
  bottom_meta: "date stamp or section marker at bottom, with hairline rule above"
}
```

### C05 — 检查清单（Checklist / Guide）

**系统**：Editorial 或 Swiss
**结构**：标题 + 4-6 行编号列表 + 每行有数字、条目、后果描述

```
composition: {
  header: "clear section title",
  rows: "4-6 numbered rows, each with index number + item title + consequence, separated by thin horizontal rules",
  style_note: "use rows/rules/columns, NOT rounded cards or generic SaaS card layouts"
}
```

### C06 — 证据墙（Evidence Wall）

**系统**：Editorial 或 Swiss
**结构**：2×2 或 3 列图片网格 + 每张图短说明 + 一个大标题锚定

```
composition: {
  grid: "2x2 or 3-column image grid, each image with short caption",
  headline: "one larger headline anchoring the interpretation",
  style_note: "images must be readable at final size, skip if not"
}
```

### C07 — 关闭笔记（Closing Note）

**系统**：Editorial
**结构**：大观点标题 + 4-6 条 ledger 行 + 底部引言/签名/CTA

```
composition: {
  title: "big takeaway title, max 2 lines",
  ledger: "4-6 items, each with title + sub-line (consequence/reason/example)",
  closing: "pull-quote OR signature line OR price/CTA at bottom"
}
```

### C08 — 数据矩阵（Swiss Data Matrix）

**系统**：Swiss
**结构**：大标题 + 网格卡片矩阵 / KPI 塔 / 横向条形图 + accent 色高亮

```
composition: {
  title: "left-aligned, light weight, extra-large",
  data_area: "card-fill matrix or KPI tower or horizontal bar chart",
  accent: "one accent color used sparingly for highlights, labels, or one emphasized data point",
  style_note: "pure blocks, hairline rules, grid rhythm, NO gradients/shadows/glass effects"
}
```

### C09 — 声明式封面（Statement Cover）

**系统**：Swiss
**结构**：一句超大声明 + 左对齐网格 + accent 色块标记

```
composition: {
  statement: "one extra-large statement, left-aligned, light font weight (the bigger the lighter)",
  accent_block: "small accent color block or bar, NOT the entire background",
  meta: "small mono metadata at bottom"
}
style_rule: "NEVER use heavy bold 80-120px text in Swiss. Larger = lighter weight is the core principle"
```

### C10 — 图片主导（Image-Led Cover）

**系统**：Editorial
**结构**：全出血大图 + 压在图上的克制标题（需图片有安静区）

```
composition: {
  image: "full-bleed photo covering entire canvas",
  title_placement: "positioned in quiet zone of photo (low-detail/uniform area)",
  typography: "restrained, NOT chunky bold caption, paper-cream text color on dark areas",
  style_note: "requires photo with quiet zone ≥30% of canvas. If no quiet zone, use C01 instead"
}
```

---

## 三、通用 Negative Prompt

所有封面共用：

```
blurry, distorted Chinese characters, wrong text, English text instead of Chinese,
watermark, logo, busy decoration, frame border, low quality, pixelated,
nested cards, rounded SaaS card layouts, random decorative SVG blobs,
heavy bold oversized titles in Swiss style, text overflow touching edge,
unreadable small text, fake data, fake version numbers
```

---

## 四、封面 Prompt JSON 模板 v2

每个 agent 的 `01_cover.prompt.md` 遵循以下结构。**`{变量}` 由脚本从 content.md 自动提取或从 TUNING.md 读取**。

```json
{
  "version": "3.0",
  "model": "gemini-image",

  "visual_system": "{VISUAL_SYSTEM}",
  "palette": "{PALETTE}",
  "layout_recipe": "{LAYOUT_RECIPE}",

  "aspect_ratio": "3:4",
  "reference_image": "reference.jpg",

  "style_prompt": "{STYLE_PROMPT}",
  "negative_prompt": "{NEGATIVE_PROMPT}",

  "title": {
    "content": "{TITLE}",
    "max_chars": 22,
    "font_style": "{TITLE_FONT}",
    "color": "{TITLE_COLOR}",
    "position": "{TITLE_POSITION}"
  },

  "subtitle": {
    "content": "{SUMMARY}",
    "max_chars": 40,
    "font_style": "{SUBTITLE_FONT}",
    "color": "{SUBTITLE_COLOR}"
  },

  "composition": "{COMPOSITION_PROMPT}",

  "fallback": {
    "no_reference": "{NO_REF_FALLBACK}",
    "text_distorted": "simplify title to 10 chars max and retry",
    "max_retries": 3,
    "final_fallback": "crop reference.jpg to 3:4 as cover"
  }
}
```

---

## 五、TUNING.md 精调变量清单

每个 agent 必须在 TUNING.md 的 `[COVER]` 区块中定义以下所有参数：

| 变量 | 说明 | 可选值 |
|---|---|---|
| `VISUAL_SYSTEM` | 视觉系统 | `editorial` / `swiss` |
| `PALETTE` | 调色板 | Editorial: `ink-classic` / `indigo-porcelain` / `forest-ink` / `kraft-paper` / `dune` / `midnight-ink`；Swiss: `ikb-blue` / `lemon-yellow` / `lemon-green` / `safety-orange` |
| `LAYOUT_RECIPE` | 布局食谱 | `C01`~`C10`（见第二节） |
| `STYLE_PROMPT` | 风格描述 prompt | 从两套系统的"prompt 关键词"中选择，可微调 |
| `NEGATIVE_PROMPT` | 反向 prompt | 默认用通用版，可追加 agent 专属禁忌 |
| `TITLE_FONT` | 标题字体风格 | Editorial: `Chinese serif (宋体/思源宋体), 400-500 weight`；Swiss: `Chinese sans-serif (黑体/Inter), 300-400 weight, the bigger the lighter` |
| `TITLE_COLOR` | 标题颜色 | 根据调色板的 `ink` 色描述，如 `deep ink black on warm paper` |
| `TITLE_POSITION` | 标题位置 | 根据布局食谱决定，如 `top 30%, left-aligned` |
| `SUBTITLE_FONT` | 副标题字体 | Editorial: `Chinese regular sans-serif`；Swiss: `mono (等宽), small` |
| `SUBTITLE_COLOR` | 副标题颜色 | 调色板的 `muted` 色 |
| `COMPOSITION_PROMPT` | 构图描述 | 从布局食谱的 composition 中选择对应描述 |
| `NO_REF_FALLBACK` | 无参考图兜底 | `pure color background from palette + text only layout` / `abstract texture matching palette mood` |

---

## 六、不可违反的铁律

### 全局铁律
1. **封面必须吃满画布** — 内容（文字+图+数据）必须覆盖 ≥75% 画布高度
2. **文字不可溢出** — 不触碰边缘，不与底部条带碰撞
3. **最小字号** — 任何文字在 1080×1440 上不得低于 26px 等效大小
4. **不造假** — 不编造数据、版本号、报价、百分比
5. **不裁人脸/关键内容** — 除非用户明确接受
6. **不可混用两套视觉系统** — 一张封面只用一种系统
7. **不可自创调色板** — 从 10 套官方色板中选

### Editorial 专属铁律
8. **不用纯色平背景** — 必须有纸纹/墨水质感层
9. **标题不压在人脸上** — 文字压图必须遵循安静区原则
10. **accent 色克制使用** — 只用于页码、分割线、或一个高亮短语

### Swiss 专属铁律
11. **越大越细** — 大标题用 300-400 weight，不用 700-900
12. **不用渐变/阴影/毛玻璃** — 纯色块、发丝线、网格节奏
13. **accent 色只用一种** — 不混合 accent 颜色

---

## 七、脚本职责（线下预处理）

生成 `01_cover.prompt.md` 的脚本：

1. **读取 TUNING.md** — 获取 `[COVER]` 区块所有精调参数
2. **从 content.md 提取标题** — 取 `# ` 开头第一行，截断到 `max_chars` 字
3. **从 content.md 提取摘要** — 正文前 100 字截断到 40 字
4. **填充模板** — 变量替换进 JSON 模板
5. **确认 reference.jpg** — 不存在则从正文首图复制
6. **写入 `01_cover.prompt.md`**

---

## 八、龙虾线上执行流程

```
1. 读取 manifest.json → 找到 slot="cover"
2. 读取 01_cover.prompt.md → 解析 JSON
3. 获取 visual_system / palette / layout_recipe
4. 加载 reference.jpg（如有）
5. 构建 Gemini Image prompt：
   - style_prompt + palette 描述 + composition 描述
   - title/subtitle 文字内容
   - negative_prompt
   - reference_image（图生图）或纯文字 prompt（文生图）
6. 调用 Gemini Image API
   - 有参考图 → image_to_image
   - 无参考图 → text_to_image
   - aspect_ratio = 3:4
7. 验证输出：
   - 中文字体无扭曲/错字 → 通过
   - 文字扭曲 → 按 fallback 重试（简化标题/截断标题）
   - 最多 3 次重试
   - 3 次失败 → reference.jpg 裁剪 3:4 作为封面
8. 上传 CDN → 回填 manifest.json
```

---

## 九、参考尺寸

| 元素 | 尺寸 | 比例 |
|---|---|---|
| 封面输出 | 1080×1440 | 3:4 竖版 |
| 公众号封面（21:9） | 2100×900 | 21:9 横版 |
| 公众号方形封面（1:1） | 1080×1080 | 1:1 |
| reference.jpg（微信封面） | 573~1280 正方形 | 1:1 |
| 正文配图（微信插图） | 1080×576 | 16:9 横版 |
