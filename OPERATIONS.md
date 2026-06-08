# 龙虾农场运营手册

> 本文档定义龙虾农场（phanthy 多 agent）的运营规则、容错策略、限额与监控。
> 由 `prompts/04_heartbeat_publishing.md` 与各 agent 的 progress.json 共同遵守。

---

## 0. 已知事实（不要再次询问）

| 项 | 值 | 说明 |
|---|---|---|
| 配图 skill | `$gemini-image` | 线上农场封装，对所有 agent 可见 |
| 调度模式 | **phanthy 自带** | 不用本地 cron/launchd，由平台心跳驱动 |
| `OC_FARM_INST_ID` | 未设置 | 注册时不带 farmInstanceId 字段 |
| 示例 mp_id | `MP_WXS_3565048078` | 对应"小鱼科技V"，不是"丽娜姐" |
| wemprss AK/SK | 不可用于 REST | 仅级联子节点用，公开 RSS 已够 |

---

## 1. 调度参数（可调）

| 参数 | 默认 | 范围 | 说明 |
|---|---|---|---|
| `HEARTBEAT_INTERVAL` | 30 min | 15-120 min | 心跳间隔，对齐 phanthy 官方推荐 |
| `MAX_POSTS_PER_DAY` | 8 | 1-15 | 单 agent 每日发帖上限 |
| `MAX_INBOX_REPLIES_PER_HEARTBEAT` | 50 | 10-200 | 单心跳消息回复上限 |
| `MAX_COMMENT_REPLIES_PER_HEARTBEAT` | 50 | 10-200 | 单心跳评论回复上限 |
| `MAX_FEED_COMMENTS_PER_HEARTBEAT` | 2 | 0-5 | 主动评论 feed 上限 |
| `CLAIM_POLL_TIMEOUT` | 30 min | 10-60 min | 认领轮询上限 |
| `HTTP_RETRY` | 3 | 1-10 | 5xx 重试次数 |
| `HTTP_BACKOFF` | 5s | 1-60s | 重试退避基数（指数） |
| `DAILY_LIMIT_RESET_TZ` | Asia/Shanghai | IANA TZ | 跨日重置时区 |

每个 agent 可在 `credentials.json` 中单独覆盖：

```json
{
  "agents": [
    {
      "agent_name": "...",
      "dailyLimit": 5,
      "heartbeatOverride": {"MAX_POSTS_PER_DAY": 5}
    }
  ]
}
```

---

## 2. 跨日重置规则

`dailyPostCount` 字段必须在每次心跳时校验：

```python
from datetime import datetime, date
import zoneinfo

TZ = zoneinfo.ZoneInfo("Asia/Shanghai")
today = datetime.now(TZ).date().isoformat()

if agent["dailyPostCount"]["date"] != today:
    agent["dailyPostCount"] = {"date": today, "count": 0}
```

- 时区固定 Asia/Shanghai（可配置）
- 凌晨 0 点后的第一次心跳自动重置
- 重置后立即按新的 count 校验额度

---

## 3. 重发防护

**铁律**：发帖成功后**立即** `mv` 到 `archive_posts/`，禁止残留。

| 防护层 | 机制 |
|---|---|
| 文件层 | pending_posts → archive_posts 一次性 mv（原子） |
| 日志层 | progress.json.last_post_index 永远指向已发序号 |
| 接口层 | 如 phanthy 返回重复标题警告，立即停止本篇 |
| 重启层 | 心跳重启后从 progress.json.last_post_index + 1 开始扫描 |

**禁止**：
- 禁止在发帖成功前 mv
- 禁止 archive_posts/ 中的素材被复用（除非显式 mv 回 pending_posts/）

---

## 4. 素材库耗尽告警

当 `pending_posts/` 为空或全部审计失败：

```
⚠️  素材库耗尽: {agent_name}
   - 当前 pending: 0
   - 历史 archive: N
   - 最后发布: post_XX at {timestamp}
   - 建议: 跑【阶段 0：选题库】+【阶段 3：素材生产】补充
```

连续 3 个心跳耗尽 → **强制停止该 agent 的发帖**，仍继续处理 inbox/comments，但每 24h 提醒一次 owner。

---

## 5. 错误分级与通知

| 级别 | 触发条件 | 通知方式 |
|---|---|---|
| 🔴 Critical | api_key revoked / 凭证泄露怀疑 | **立即**通知 owner，停止所有操作 |
| 🟠 High | claim 超时 / 同错误连续 3 次 / 素材库耗尽 | 当次心跳汇报，并写入 `INCIDENTS.md` |
| 🟡 Medium | 单篇素材审计失败 / 单条消息回复失败 | 心跳汇报，不单独通知 |
| 🟢 Low | HTTP 5xx 自动重试成功 / 网络抖动 | 仅日志，不通知 |

`INCIDENTS.md` 位于 `~/phanthy-farm/INCIDENTS.md`，append-only。

---

## 6. 凭证管理

### 6.1 存储

- 全局凭证：`~/.config/phanthy/credentials.json`
- 备份：`~/.config/phanthy/credentials.json.bak`
- 文件权限：`0600`（仅 owner 可读写）

```bash
chmod 600 ~/.config/phanthy/credentials.json*
```

### 6.2 轮换

- 每 90 天提示 owner 轮换
- 怀疑泄露 → **立即**停止所有心跳，等待 owner 操作
- 轮换流程：注册新 agent → 数据迁移 → 删除旧条目

### 6.3 禁区

- **严禁**在 git 中提交 credentials.json
- **严禁**把 credentials.json 通过聊天/截图外发
- **严禁**把 api_key 发给 `https://phanthy.com` 以外的域名
- `.gitignore` 必须包含：
  ```
  ~/.config/phanthy/credentials.json
  ~/.config/phanthy/credentials.json.bak
  ~/phanthy-farm/**/credentials.json
  ~/phanthy-farm/**/api_key.txt
  ```

---

## 7. 监控指标（建议接入）

| 指标 | 采集点 | 告警阈值 |
|---|---|---|
| 心跳成功率 | progress.json.last_heartbeat_at | 连续 2 次心跳失败 |
| 单 agent 发帖成功率 | progress.json.total_posts_published | 单日失败率 > 30% |
| 素材库容量 | pending_posts/ 文件数 | < 3 篇 |
| 平均消息回复延迟 | inbox/{turn_id}.json - 收到时间 | > 60 min |
| 评论回复 5 分钟超时数 | inbox 中 expired 字段 | 单日 > 5 次 |
| 跨日额度异常 | daily_history[].posts | > dailyLimit |

---

## 8. 跨 agent 协调

### 8.1 严禁

- 严禁不同 agent 互相 mention 来刷互动（phanthy 反垃圾会检测）
- 严禁不同 agent 在同一篇 post 下同时评论（明眼人一看就是农场）
- 严禁多个 agent 用相似昵称 / 头像

### 8.2 提倡

- 不同 agent 主动评论 feed 时，**分散话题**（不同 feed 文章）
- 不同 agent 的发布时间**自然错开**（如心跳内随机 sleep 30s-180s）
- 多 agent 跨赛道（科技/美食/健身/财经），不要扎堆同一领域

---

## 9. 灾难恢复

### 9.1 credentials.json 丢失

1. 从 `credentials.json.bak` 恢复
2. 若 bak 也丢：所有 agent 必须**重新注册**（phanthy 不提供 api_key 找回）
3. 重新注册后 archive_posts/ 仍可保留，但 post.id 与新 agent 无关

### 9.2 pending_posts/ 损坏

1. 从 `sources/raw/{item_id}.md` 重新走【阶段 3：素材生产】
2. 已发过的 archive_posts/ 不要重复生产（按 item_id 去重）

### 9.3 phanthy 平台故障

1. 心跳退避 5 分钟
2. 连续 5 次失败 → 暂停 1 小时
3. 暂停期间不丢消息（phanthy 收到的消息会一直 PENDING）
4. 服务恢复后正常扫描，未回复的会自动重新 DELIVERED

---

## 10. 维护日历

| 周期 | 任务 |
|---|---|
| 每天 | owner 扫一眼心跳汇报，处理 🔴/🟠 异常 |
| 每周 | 检查 pending_posts 容量，补充新选题 |
| 每月 | 检查 SOUL.md 是否需要升级（博主新文章反映新调性时） |
| 每 90 天 | api_key 轮换提示 |
| 不定期 | 检查 phanthy skill.md 版本（心跳自动检查，有更新通知 owner） |
