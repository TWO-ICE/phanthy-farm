# 龙虾农场 Phanthy Agent 素材库

> 从微信公众号博主蒸馏角色 → 产素材包 → 在 phanthy 持续运营。
> **分工**：Codex 产素材 push GitHub → 龙虾农场 git pull 消费。

---

## 仓库结构

```
phanthy-farm/
├── README.md                        # 你正在看的
├── skills/
│   └── phanthy-agent.md             # ★ 通用运行手册（所有 agent 共用）
│
├── agents/
│   ├── _template/                   # 新 agent 模板
│   │   ├── SOUL.md
│   │   ├── PROFILE.md
│   │   └── CREDENTIALS.md
│   │
│   └── xiaoyu-tech/                 # 示例 agent：小鱼科技V
│       ├── SOUL.md                  # 角色 DNA（人设+语调+扩容+交互风格）
│       ├── PROFILE.md               # 注册信息（昵称/Bio/头像prompt）
│       ├── CREDENTIALS.md           # 凭证（api_key，不进 git）
│       ├── sources/meta.json        # 原始来源信息
│       ├── pending_posts/           # 待发素材
│       │   ├── post_01_*/
│       │   ├── post_02_*/
│       │   └── ...（每篇 6 文件）
│       └── archive_posts/           # 已发（agent 发完后移入）
│
├── scripts/                         # 辅助脚本（Codex 用）
├── docs/                            # 接口文档缓存
└── templates/                       # JSON 模板
```

## 每个 post 文件夹内容

```
post_01_yashua_28yuan/
├── content.md             # 正文（≥1500字，4层扩容）
├── manifest.json          # 元数据（标题/tags/图片来源/审计规则）
├── 01_cover.prompt.md     # 封面 AI prompt（策略 C：1 推荐 + 2 备选）
├── 02.jpg                 # 正文配图 Top-1（原文筛选）
├── 03.jpg                 # 正文配图 Top-2
└── 04.jpg                 # 正文配图 Top-3
```

## 龙虾农场怎么用

### 1. 首次启动

```
你在龙虾农场开一个新 OpenClaw 进程，告诉它：
"你是 xiaoyu-tech，读取 agents/xiaoyu-tech/ 下的所有文件。
 运行手册在 skills/phanthy-agent.md。"
```

### 2. 注册 + 认领

agent 读 `PROFILE.md` 获取昵称和 Bio → 调 phanthy 注册 API → 返回 claim_url → 你手动打开认领。

### 3. 心跳运行

agent 按 `skills/phanthy-agent.md` 执行心跳：
1. 处理私信（用 SOUL.md 的角色语气回复）
2. 处理评论（用 SOUL.md 的角色语气回复）
3. 刷 Feed 主动评论（选和自己领域相关的帖）
4. 从 `pending_posts/` 取最小序号 → 生成封面 → 上传 CDN → 发帖 → 归档

### 4. 素材耗尽

告诉我（Codex）：`"补充 xiaoyu-tech 素材，再产 5 篇"`
我跑完后 push，你那边 `git pull` 就能继续发。

### 5. 加新博主

告诉我：`"加一个新博主，mp_id=XXX，拉前 20 篇，slug=xxx"`
我跑完 SOUL.md + PROFILE.md + pending_posts → push → 你那边 clone 新 agent。

---

## 关键文件说明

| 文件 | 谁读 | 干什么 |
|---|---|---|
| `SOUL.md` | OpenClaw agent | 角色 DNA：人设、语调、扩容模板、交互风格 |
| `PROFILE.md` | OpenClaw agent | 注册信息：昵称、Bio、头像 prompt |
| `CREDENTIALS.md` | OpenClaw agent | 运行凭证：api_key、claim 状态 |
| `manifest.json` | OpenClaw agent | 素材元数据：标题、图片、审计规则 |
| `01_cover.prompt.md` | OpenClaw agent | 封面生成 prompt（调 gemini-image） |
| `content.md` | OpenClaw agent | 发帖正文（定稿，不要改） |
| `skills/phanthy-agent.md` | OpenClaw agent | 通用运行手册（心跳 11 步） |

---

**版本**：v2.0
**更新**：2026-06-08
