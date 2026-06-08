---
agent_slug: susu-fashion
agent_name: 苏苏姐家
agent_type: crochet_shop  # 原创钩织 e-commerce
article_count: 118
status: active  # active / dormant / v1_legacy

# 继承 /AGENT_RULES.md 默认
image_pipeline:
  top_n_download: 16          # override 12 (单篇 24-42 张图)
  min_file_size: 6000         # override 8000
  filter_banner_height: 400

content:
  skeleton: [A, B, C]         # override "free"
  min_chars: 1500
  voice_notes: |
    花园系产品名 (必须解释命名故事) + 织女社群口吻 + 大量留白 (≥4 处) +
    收尾必含「以 手 造 物丨以 物 寄 情」+「愿一切真心不被辜负...」
    句长 5-15 字, 收尾用 ~~/../~ 波浪

cover:
  palette: cream + oatmeal + dried_rose + sage_green
  forbidden: [neon, plastic_texture, 3D_shadow, busy_decoration]
---

# AGENT_RULES.md — 苏苏姐家

> 精调自 [通用规则](/AGENT_RULES.md)

## 简介

苏苏姐家 = 原创钩织工坊（江浙），主营手作衣服 / 包包 / 家居小物，附视频教程 + 达人作品欣赏。

- mp_id: `MP_WXS_3550746681`
- 文章数: 118
- 风格: 花园系产品名 + 织女社群 + 慢生活治愈 + 大量留白

## 继承

完全继承 [通用规则](/AGENT_RULES.md)。

## 精调

### 拉素材

- `top_n`: 5（新 agent 默认）
- 推荐 batch: 10-15（一次性多备，避免 RSS 限 30）
- **特别注意**：苏苏姐家 RSS 含大量「入会即享」重复短文（<500 字）
  - 过滤策略：选 `char_count` 最高的 5 篇
  - 重复短文特征：标题完全相同 + 内容 < 500 字 + 末尾是原创声明 + 品牌小诗

### 图片 Pipeline

- `top_n_download`: **16**（单篇 24-42 张图，12 张不够）
- `min_file_size`: **6000**（苏苏姐家有些装饰小图是 4.8KB，警戒线收紧）
- 横幅过滤：高度 < 400px 的产品对比图跳过（如 1080×330、750×269、750×360）
- pHash 距离 ≤ 8 视为重复
- **必用** `expand_body_images.py` 二阶段拉取

### Content 写作

- `skeleton`: 三种混用
  - A. 月度合集型（如「5月新品合集」）
  - B. 今日新品型（如「今日新品 | XX + YY」）
  - C. 达人专访型（如「实践出针织 | 达人作品欣赏」）
- `min_chars`: 1500
- **必须解释每个产品名的命名故事**（苏苏姐家的灵魂 — 花园系）
- **收尾必含**「以 手 造 物丨以 物 寄 情」+「愿一切真心不被辜负，愿一切努力终有收获，愿一切如你所愿」
- 留白 ≥ 4 处（苏苏姐家风格特别爱留白）
- 句长 5-15 字
- 收尾常用：`~~` 双波浪 / `..` 双点 / `~` 单波浪
- 段落用 `---` 分隔，钩子用 `**` 加粗
- **禁忌**：限时 / 秒杀 / 速来 / 加微 / 私聊 / 群内 / 福利 / 冲冲冲 / 集美们 / 绝绝子 / 高级感 / 轻奢

### Cover Prompt

- 色调: 奶油白 + 燕麦 + 干玫瑰粉 + 鼠尾草绿（江浙工坊感）
- 禁止: 霓虹色、塑料感、3D 阴影、繁忙装饰、frame border
- 必须: 3:4 竖版、img2img、reference.jpg
- 占位符: `{TITLE}` / `{SUBTITLE}` / `{PRICE}` 已预填
- price_tag 用矩形圆角（非圆/星）

### 已知坑

- 单篇 24-42 张图，12 张选择池太小，**必用** `expand_body_images.py` 二阶段
- 月度合集文（4990 字）通常 8 件产品，写作时挑 3-4 件深度讲即可
- 达人专访文（2271 字）5 位达人，每位 1 段
- 入会即享文（406 字 ×多）跳过，不做 post

## 状态

- 创建: 2026-06-08
- 已产 post: 5（post_01..05）✅
- 图片池扩展: commit `1b40b4e` ✅
- 下次产 post: 待定（备 5-10 篇 char_count 最高的）
- 仓库 commits:
  - `2bd472f` feat: 新 agent susu-fashion (5 个 post 全部审计通过)
  - `1b40b4e` feat(susu-fashion): 扩展正文图片池 - Top-3 from 12
