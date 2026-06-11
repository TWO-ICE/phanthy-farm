# Agent 规则：onehu-zhihu（一壶盐选）

> 本文件定义此 agent 的目录结构、状态流转和核心规则。
> 与 SOUL.md（人设/语气）、TUNING.md（仿写/封面/配图参数）、BOOT.md（启动流程）配合使用。

## 目录结构（v2）

```
agents/onehu-zhihu/
├── AGENT_RULES.md    ← 本文件：通用规则
├── TUNING.md         ← 精调文档：仿写策略、封面设计、正文配图等个性化配置
├── SOUL.md           ← 人设：说书人语调、回复私信/评论/Feed 风格
├── PROFILE.md        ← 注册信息：昵称、Bio、头像 prompt、备选
├── BOOT.md           ← 启动配置：注册流程、心跳循环、审计规则
├── CREDENTIALS.md    ← 凭证（不进 git）
├── 款式3_3x4.png     ← 封面/正文图共用背景
│
├── draft/            ← 原料仓（2945 篇，等待加工）
│   └── post_XXX_<标题>/
│       └── source.md
│
├── post/             ← 成品仓（加工完成，可直接发布）
│   └── post_XXX_<标题>/
│       ├── content.md     ← 仿写完成的正文（标题 + 全文 + 溯源）
│       ├── cover.png      ← 封面图（896×1200px）
│       └── body_pages/    ← 正文图片（最多 20 张 PNG）
│           ├── page_001.png
│           └── ...
│
└── archive_posts/    ← 已发布归档（发帖成功后从 post/ 移入）
    └── post_XXX_<标题>/
```

## 状态流转

1. **入仓**：清洗好的 source.md → `draft/post_XXX_标题/`
2. **加工**：从 draft 选题 → 仿写 + AI 起标题 + 生成封面 + 生成正文图 → 移入 `post/`
3. **消费**：线上从 `post/` 取内容发布 → 发帖成功后移入 `archive_posts/`

### 加工流水线

```
draft/source.md
    ↓ salt_rewrite.py（glm-4.7 仿写，12000 字基准）
post/content.md
    ↓ glm-4-flash 起新标题（≤15 字书名式）
post/content.md（标题更新）
    ↓ cover_generator.py（v9 封面规范）
post/cover.png
    ↓ body_image_generator.py（正文分页图，≤20 张）
post/body_pages/page_001.png ~ page_NNN.png
    ✅ 完成，可发布
```

## 命名规则

- 文件夹格式：`post_XXX_<标题>`
- 编号从 001 起递增，不重复
- 标题去特殊字符，保留中文/字母/数字
- 标题必须是书名式（≤15 字），不要知乎问句格式

## 核心原则

- `draft/` 里只有 source.md（原料）
- `post/` 里是完整可发布的内容（成品）
- `archive_posts/` 里是已发布的帖子
- **位置即状态**，不靠文件名后缀标记
- 每次加工按需选题，不强制全跑
- 每次心跳只发 1 个 post，从 post/ 取序号最小的
- 发帖前必须审计：content.md + cover.png + body_pages/ 三件套齐全

## 内容画像

- 2945 篇知乎盐选小说
- 类型覆盖：言情/虐恋/悬疑/古言/灵异/穿越/修仙/科普/历史
- 平均字数 ~18500 字
- 字数分布：41% 在 12K-20K，25% 在 20K-40K
- 仿写后目标：短文扩到 12000 字，长文保持 ±10%
