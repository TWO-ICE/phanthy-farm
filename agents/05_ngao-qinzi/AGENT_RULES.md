# Agent 规则：ngao-qinzi（年糕亲子生活）

## 目录结构（v2）

```
agents/ngao-qinzi/
├── AGENT_RULES.md    ← 本文件
├── TUNING.md         ← 精调文档
├── SOUL.md           ← 角色DNA
├── PROFILE.md        ← 注册信息
├── CREDENTIALS.md    ← 凭证（待填）
├── draft/            ← 原料仓（911篇）
└── post/             ← 成品仓
```

## 状态流转

```
draft/ → [仿写+AI标题] → [封面生成] → [正文图生成] → post/ → git push
```

## 核心原则

- 位置即状态：draft/ = 原料，post/ = 成品
- 每篇 post 三件套：content.md + cover.png + body_pages/
- 仿写字数基准：1500字
- 按需从 draft 取材，不强制全跑
