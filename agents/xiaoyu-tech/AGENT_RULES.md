---
agent_slug: xiaoyu-tech
agent_name: 小鱼科技V
agent_type: tech_deals  # 二手捡漏博主
article_count: 928
status: v1_legacy  # v1 旧规范 (4 层模板), 不再生产新内容
---

# AGENT_RULES.md — 小鱼科技V

> 精调自 [通用规则](/AGENT_RULES.md)

## 简介

小鱼科技V = 二手捡漏 / 数码测评博主（v1 旧规范，30 个 post 已完成）。

- mp_id: `MP_WXS_3565048078`
- 文章数: 928
- 风格: 二手捡漏 + 数码推荐 + 实测

## 继承

完全继承 [通用规则](/AGENT_RULES.md)。

## 精调

### v1 旧规范

- **30 个 post 已用 v1 4 层模板**（观点/数据/案例/落地）
- v2 升级：**未做**（用户没要求重做）
- 新内容生产：**暂停**（除非用户明确要求按 v2 重做）

### 如需重做 v2

按 [通用规则](/AGENT_RULES.md) 的 9 节 SOUL 模板 + 阶段 3 的 v2 content.md 规范重写。
不需要保留 v1 4 层结构。

## 已知坑

- 文章数量大（928 篇），RSS 限 30。需要时分批拉或用 Tier 2 全量导出
- v1 4 层标记词在 audit 里只是 warning，不阻塞；v2 已废除

## 状态

- v1 已完成 30 post ✅
- v2 升级: ❌ 未做
- 下次操作: 待用户指示
- 仓库 commits:
  - `161d900` docs: xiaoyu-tech 专属 AGENT_PROMPT.md（493 行）
