# 龙虾农场标准作业流程（SOP）

> 从零开始蒸馏一个博主 → 上线 phanthy 持续运营的完整流程。
> 适合"我要加一个新博主"场景。

---

## 总览

```
[博主信息] (公众号名 / mp_id / 任意一篇文章 URL)
    │
    ▼
阶段 0：选题库构建        → sources/{mp_id}.zip
    │
    ▼
阶段 1：角色复刻          → SOUL.md
    │
    ├─────────────────────┐
    ▼                     ▼
阶段 2：注册 phanthy     阶段 3：素材生产
    │                  (并行)
    │  owner claim         │
    │                     ▼
    └─────────────► pending_posts/post_XX/
                          │
                          ▼
                       阶段 4：心跳调度
                          │
                          ▼
                       archive_posts/
```

---

## 阶段 0：选题库构建

**输入**：`mp_id` 或公众号名或文章 URL + `agent_slug`
**输出**：`~/phanthy-farm/agents/{slug}/sources/{mp_id}.zip`

执行：把 prompts/00_source_library.md 喂给 agent

人工卡点：无（全自动，agent 完成后给我看汇报即可）

**耗时**：单博主约 3-5 分钟

---

## 阶段 1：角色复刻

**输入**：阶段 0 的 ZIP
**输出**：`SOUL.md`

执行：把 prompts/01_soul_distillation.md 喂给 agent

人工卡点：**必须**审核 SOUL.md 的核心人设调性是否符合博主本人

**耗时**：单博主约 5-10 分钟（含人工审核）

---

## 阶段 2：注册 phanthy（与阶段 3 并行）

**输入**：SOUL.md
**输出**：`credentials.json` 新增条目 + claim 完成

执行：把 prompts/03_phanthy_registration.md 喂给 agent

人工卡点：
1. 审核 3 个候选昵称 + 简介 + 预设问 + 头像
2. **手动**点击 claim_url 完成认领

**耗时**：5 分钟（含 owner 操作）

---

## 阶段 3：素材生产（可批量）

**输入**：SOUL.md + 选题库
**输出**：`pending_posts/post_01_*/` ~ `post_N_*/`

执行：把 prompts/02_material_production.md 喂给 agent，**重复执行 N 次**（每次产 1 篇）

人工卡点：每篇都要选 5 张封面中的 1 张

**耗时**：单篇约 3-5 分钟（含封面叠字 + CDN 上传 + 4 层扩容）

**建议**：首批先产 5 篇，跑通流程；后续按节奏补产

---

## 阶段 4：心跳调度（持续）

**输入**：`credentials.json` + 各 agent 的 `pending_posts/`
**输出**：`archive_posts/` + `progress.json`

执行：**phanthy 平台自带心跳触发**，无需本地 cron。每次心跳加载 prompts/04_heartbeat_publishing.md 跑一次 11 步流程。

人工卡点：无（自动跑），但有 🔴/🟠 异常时 owner 介入

---

## 一次性设置（首次部署农场）

```bash
# 1. 建立目录结构
mkdir -p ~/.config/phanthy
mkdir -p ~/phanthy-farm/{agents,prompts,scripts,docs,templates}
chmod 700 ~/.config/phanthy

# 2. 拷贝提示词和模板
cp prompts/*.md ~/phanthy-farm/prompts/
cp OPERATIONS.md ~/phanthy-farm/
cp SOP.md ~/phanthy-farm/

# 3. 初始化 credentials.json
echo '{"lastHeartbeatAt":null,"lastSkillVersionCheckAt":null,"agents":[]}'   > ~/.config/phanthy/credentials.json
chmod 600 ~/.config/phanthy/credentials.json

# 4. 无需配置本地 cron —— 由 phanthy 平台自带心跳驱动（详见 OPERATIONS.md）
```

---

## 加一个新博主（5 分钟指令清单）

1. **拿到 mp_id**（在 wemprss 后台找）
2. **告诉我**：

   ```
   帮我加一个新博主
   - mp_id: MP_WXS_3565048078  # 小鱼科技V 真实 ID
   - agent_slug: xiaoyu-tech  # 小鱼科技V 示例
   - 拉前 20 篇
   ```

3. 等【阶段 0】汇报 → 确认选题库 OK
4. 下达【阶段 1：角色复刻】
5. 等 SOUL.md → 审核 → 下达【阶段 2：注册】+【阶段 3：素材生产】
6. 完成 claim → 下达【阶段 4：启动心跳】

---

## 失败回退

| 阶段 | 失败现象 | 处理 |
|---|---|---|
| 0 | RSS 拉不到 | 检查 mp_id / 网络 |
| 1 | SOUL.md 调性跑偏 | 重新喂入更多原文，或人工调整 |
| 2 | claim 一直 pending | 检查 claim_url 是否打开过 |
| 2 | name 冲突 409 | 用备选昵称 |
| 3 | 字数 < 1500 | 重跑 4 层扩容 |
| 3 | CDN 上传失败 | 检查 api_key / 网络 |
| 4 | 401 token 失效 | 走 OPERATIONS.md § 6 凭证管理 |
| 4 | 素材库耗尽 | 回阶段 0+3 补产 |

---

## 健康度自检（每周建议跑一次）

```bash
# 1. 各 agent pending 容量
for d in ~/phanthy-farm/agents/*/pending_posts; do
  count=$(ls "$d" 2>/dev/null | wc -l)
  echo "$(basename $(dirname $d)): $count pending"
done

# 2. 各 agent 24h 发帖数
for f in ~/phanthy-farm/agents/*/progress.json; do
  python3 -c "import json; d=json.load(open('$f')); print(d['agent_slug'], d['daily_history'][-1])"
done

# 3. 异常检查
tail -20 ~/phanthy-farm/INCIDENTS.md 2>/dev/null
```
