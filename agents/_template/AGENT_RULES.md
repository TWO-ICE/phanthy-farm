---
# 这是模板, 实际 agent 复制本文件到 agents/<slug>/AGENT_RULES.md 后改名 + 填字段
agent_slug: _template
agent_name: {你的 agent 名字}
agent_type: {类别, e.g. crochet_shop / fitness / gossip / tutorial}
article_count: 0
status: draft   # draft | active | dormant | v1_legacy

# 继承 /AGENT_RULES.md 默认。除非下方明确列出, 都按默认来。
image_pipeline:
  # top_n_download: 12          # 默认 12
  # min_file_size: 8000         # 默认 8000
  # min_dim: 400                # 默认 400
  pass

content:
  # skeleton: [A, B, C]         # 默认 "free", 可选 A/B/C/D
  # min_chars: 1500             # 默认 1500
  # voice_notes: ""             # 留空
  pass

cover:
  # palette: ""                # 留空, 走 SOUL.md 的设定
  # forbidden: []               # 留空
  pass
---

# AGENT_RULES.md — {agent_name}

> 精调自 [通用规则](/AGENT_RULES.md)
>
> **使用方式**：复制本文件到 `agents/<your-slug>/AGENT_RULES.md`, 改 `agent_slug` + `agent_name` + 删注释行 (`#`) + 填入精调字段。

## 简介

{一段话描述这个 agent 是什么, 主营什么, 风格如何}

- mp_id: `MP_WXS_xxx`
- 文章数: 0
- 状态: draft

## 继承

完全继承 [通用规则](/AGENT_RULES.md) 的所有默认。

除非下方 front matter 明确列出, 都按 base 默认来。

## 精调（按需填写）

### 拉素材

- `top_n`: 5 (新 agent 默认)
- 推荐 batch: 10-15 (一次性多备, 避免 RSS 限 30)
- 去重: 选 char_count 最高的 N 篇

### 图片 Pipeline

- `top_n_download`: 12 (默认)
- `min_file_size`: 8000 (默认)
- 横幅过滤: 高度 < 400px 的产品对比图跳过（如 `expand_body_images.py` 默认）
- pHash 距离 ≤ 8 视为重复

### Content 写作

- `skeleton`: free (默认, 可选 A.月度合集 / B.今日新品 / C.达人专访 / D.自由)
- `min_chars`: 1500 (默认)
- voice_notes: {agent 特有风格描述}

### Cover Prompt

- 色调: {走 SOUL.md 的设定}
- 禁止: {霓虹色 / 塑料感 / 3D 阴影 / 繁忙装饰}

## 已知坑

{任何 agent 特有的注意事项, 例如:
- 单篇图密度高, 必用 expand_body_images.py 二阶段
- 月度合集文常 8+ 件产品, 写作时挑 3-4 件深度讲即可
- ...}

## 状态

- 创建: {ISO date}
- 已产 post: 0 / pending
- 下次产 post: {填入计划日期或 "待定"}
