---
agent_slug: xiaoyu-tech
agent_name: 小鱼科技V
agent_type: tech_deals  # 二手捡漏博主
article_count: 921
status: v2_active  # v2 新规范 (3 步洗稿法), 正在生产内容
---

# AGENT_RULES.md — 小鱼科技V

> 精调自 [通用规则](/AGENT_RULES.md)

## 简介

小鱼科技V = 二手捡漏 / 数码测评博主（v2 新规范，pending_posts 共 921 篇）。

- mp_id: `MP_WXS_3565048078`
- 文章数: 921（清洗后）
- 风格: 二手捡漏 + 数码推荐 + 实测

## 继承

完全继承 [通用规则](/AGENT_RULES.md)。

## 精调

### v2 新规范（当前生效）

- **pending_posts 共 921 篇**（post_31 - post_951）
- 每篇 6 文件包：`content.md`（LLM 深度仿写）+ `manifest.json` + `01_cover.prompt.md` + `reference.jpg`（原文封面）+ `img_*.jpg`（正文图 1-N 张，已裁 20%）
- 状态机：文件夹名以"完"结尾 = 可发；`MISSING_IMGS` 标记 = 缺图待补
- LLM 仿写规则：3 步洗稿法（语料脱水 → 骨架映射 + 风格平移扩容 → 格式封装），字数 1500-2200

### v1 旧规范（已废弃）

- v1 4 层模板（观点/数据/案例/落地）：**已废弃**，不再生产
- v1 旧 30 个 post：**已删除**（从 pending_posts 清除）

## 已知坑

- 文章数量大（921 篇），complete 需分批跑
- 图过滤阈值严：约 25% post 会触发 `all_body_imgs_failed`，标 MISSING_IMGS 需单独补图
- 内容 MD 跟原文同源：标题锁定为 source.md 标题，LLM 不能改

## 状态

- v2 启动: ✅（2026-06-09）
- 当前 done: 42 / 921
- 缺图 post: 13（MISSING_IMGS 状态）
- 下次操作: 等 50 篇人工验收后批量跑剩余 866 篇
- 仓库 commits:
  - `161d900` docs: xiaoyu-tech 专属 AGENT_PROMPT.md（493 行）
