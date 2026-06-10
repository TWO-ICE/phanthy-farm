# Agent 规则：onehu-zhihu

## 目录结构（v2）

```
agents/onehu-zhihu/
├── AGENT_RULES.md    ← 本文件：通用规则
├── TUNING.md         ← 精调文档：仿写策略、封面、配图等个性化配置
├── SOUL.md           ← 人设
├── PROFILE.md        ← 简介
├── BOOT.md           ← 启动配置
├── CREDENTIALS.md    ← 凭证
│
├── draft/            ← 原料仓（等待消耗）
│   └── post_XXX_<标题>/
│       └── source.md
│
└── post/             ← 成品仓（可直接发布）
    └── post_XXX_<标题>/
        ├── content.md
        ├── manifest.json
        └── ...（按需）
```

## 状态流转

1. **入仓**：清洗好的 source.md → `draft/post_XXX_标题/`
2. **加工**：从 draft 选题 → 仿写/补内容 → 移入 `post/`
3. **消费**：线上从 `post/` 取内容发布

## 命名规则

- 文件夹格式：`post_XXX_<标题>`
- 编号从 001 起递增，不重复
- 标题去特殊字符，保留中文/字母/数字

## 核心原则

- `draft/` 里只有 source.md（原料）
- `post/` 里是完整可发布的内容（成品）
- 位置即状态，不靠文件名后缀标记
- 每次加工按需选题，不强制全跑
