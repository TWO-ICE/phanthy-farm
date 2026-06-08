# AGENT_RULES.md — Phanthy Farm 通用规则 (BASE)

> **本文件是所有 agent 的根规则**。每个 agent 通过 `agents/<slug>/AGENT_RULES.md` 精调覆盖部分字段。
>
> **执行者必读** — 任何 Codex / Hermes / 人在动手前必须：
> 1. `git pull` 拿最新
> 2. 读本文件
> 3. 读目标 agent 的 `agents/<slug>/AGENT_RULES.md`
> 4. `git status` 看哪个 agent 准备到哪一步
> 5. `python3 scripts/audit_pending.py --agent-slug <slug>` 看 audit 状态
> 6. 再开始执行

---

## 1. 5 阶段流水线

每个 agent 的内容生产 = 5 个阶段：

| 阶段 | 名字         | 产出                                       | 工具                       |
|------|--------------|--------------------------------------------|----------------------------|
| 0    | 拉素材       | `sources/raw/{item_id}.md` + `.jpg`        | `scripts/fetch_rss.py`     |
| 1    | 蒸馏 SOUL    | `SOUL.md` (v2 3 步洗稿法，9 节)            | 人工 + 经验                |
| 2    | 注册资产     | `PROFILE.md` / `BOOT.md` / `CREDENTIALS.md` | 人工                       |
| 3    | 产 Post      | `pending_posts/post_XX_*/` 6 文件          | `scripts/build_cover_prompt.py` |
| 4    | 心跳         | (OpenClaw 侧，与 Codex/Hermes 无关)        | `skills/phanthy-agent.md`  |

本规则只覆盖阶段 0-3。阶段 4 由 `skills/phanthy-agent.md` + OpenClaw 负责。

---

## 2. Pre-flight 必做

任何 agent 操作前：

```bash
# 1. 拉最新规则
cd /path/to/template/repo && git pull

# 2. 读 2 份规则
cat AGENT_RULES.md                          # 本文件
cat agents/$SLUG/AGENT_RULES.md             # 目标 agent 的精调

# 3. 加载合并后的规则（可选）
python3 scripts/load_rules.py $SLUG

# 4. 看状态
ls agents/$SLUG/pending_posts/              # 待发
ls agents/$SLUG/archive_posts/              # 已发
git log --oneline -5 agents/$SLUG/          # 最近变更

# 5. 跑 audit 看是否已就绪
python3 scripts/audit_pending.py --agent-slug $SLUG
```

---

## 3. 仓库结构（每个 agent 必含）

```
agents/<slug>/
├── SOUL.md                  ← 9 节（v2 3 步洗稿法）
├── PROFILE.md               ← name/desc/头像 prompt/3 预设问
├── BOOT.md                  ← 启动指令（OpenClaw 用）
├── CREDENTIALS.md           ← 注册后填写（不进 git）
├── AGENT_RULES.md           ← 精调覆盖（必含 front matter）
├── sources/
│   ├── meta.json            ← 拉取元数据
│   ├── raw/{item_id}.md     ← 单篇原文 markdown
│   ├── raw/{item_id}/       ← 单篇原文图片（cover + img_1/2/3）
│   └── MP_WXS_xxx.zip       ← 打包（不进 git）
├── pending_posts/           ← 待发（按 post_01, post_02 顺序）
│   └── post_XX_<slug>/
│       ├── content.md
│       ├── manifest.json
│       ├── 01_cover.prompt.md
│       ├── reference.jpg
│       ├── 02.jpg
│       ├── 03.jpg
│       └── 04.jpg
└── archive_posts/           ← 已发（按 post_XX 时间归档）
```

---

## 4. 命名约定

- `slug`：mp_name 转 pinyin 或英文（例：「苏苏姐家」→ `susu-fashion`）
- `post_XX_<short_title>`：序号 + 短标题（例：`post_01_5月新品合集`）
- 文件名不空格，用 `_` 或 `-` 连接
- 短标题 ≤ 12 个汉字，避免过长目录名

---

## 5. 阶段 0：拉素材

### 5.1 方式选择

| 方式         | 限制             | 适用                     |
|--------------|------------------|--------------------------|
| A. RSS       | limit ≤ 30       | 5-30 篇                  |
| B. Tier 2    | 全部（异步）     | 大量原文                 |
| C. Tier 3    | offset/limit     | 跳过前 N 篇，拿后续       |

**默认走方式 A（RSS）**，单 mp 5 篇就够 1 个 batch。

### 5.2 fetch_rss.py 命令

```bash
python3 scripts/fetch_rss.py \
  --mp-id MP_WXS_xxx \
  --agent-slug your-slug \
  --top-n 5
```

### 5.3 去重策略

如果 RSS 里出现重复短文（如某商家的「入会即享」×N），选 `char_count` 最高的 N 篇。

### 5.4 凭证要求

- 方式 A 公开 RSS：**不需要** wemprss 凭证
- 方式 B / C：需要 wemprss OAuth2 token（用户名密码登录拿）

---

## 6. 图片处理 Pipeline（阶段 0 核心）

### 6.1 六步流程

1. **URL 启发式过滤**（下载前）
   - 排除：`qrcode` / `qr_noroaming` / `biz_qr` / `mmbiz_qrcode`（二维码）
   - 排除：`biz_head` / `headimg`（公众号名片）
   - 排除：`placeholder` / `default_cover`（占位图）
   - 排除：`.gif` / `mmbiz_gif`（GIF 表情）
2. **下载**：走 wemprss image proxy + 自动裁下方 20% 去公众号水印
3. **下载后内容过滤**：
   - 文件 < `min_file_size`（默认 8000B）视为损坏
   - 尺寸 < `min_dim`（默认 400px）任一边视为缩略图/横幅
   - 像素灰度标准差 < `blank_std_threshold`（默认 8.0）视为空白/纯色
   - perceptual hash 距离 ≤ `phash_hamming_max`（默认 8）视为重复
4. **评分**（沿用 `pick_top3_images`）：
   - 尺寸 ≥ 600×400：+3
   - 比例接近 16:9 / 4:3 / 1:1 / 3:2：+2
   - `mmbiz_jpg` / `mmbiz_png`：+1
   - 位置靠后：+1
   - alt 非广告：+1
   - URL 含 `640` / `article` / `content`：+1
5. **选 Top-K**：K = `final_top_k`（默认 3）
6. **替换** `02/03/04.jpg`（或更多，agent 精调）

### 6.2 默认参数

| 参数                      | 默认值   | 说明                       |
|---------------------------|----------|----------------------------|
| `top_n_download`          | 12       | 下载张数（选 K=3）         |
| `min_file_size`           | 8000     | 文件大小下限（字节）       |
| `min_dim`                 | 400      | 尺寸下限（px）             |
| `blank_std_threshold`     | 8.0      | 空白判定的灰度标准差阈值   |
| `phash_hamming_max`       | 8        | pHash 重复判定的汉明距离   |
| `final_top_k`             | 3        | 最终选 K 张                |

### 6.3 二阶段拉取（image-heavy MPs）

如果单篇图 ≥ 20 张（如苏苏姐家 24-42 张），单 Top-3 选得太窄。
用 `scripts/expand_body_images.py` 二阶段重拉：

```bash
/usr/bin/python3 scripts/expand_body_images.py --agent-slug X --all --top-n 16
```

> **⚠️ 必须用 `/usr/bin/python3`**（hermes sandbox Python 无 PIL，系统 Python 3.9.6 有）

### 6.4 路径注意

- 运行时目录：`~/phanthy-farm/agents/<slug>/`
- 模板仓库：`/Users/<user>/Documents/phanthy/agents/<slug>/`
- **任何 git 操作前必须 cd 模板仓库**
- **写完 runtime 必须 rsync 到模板仓库**

```bash
rsync -av --delete \
  --exclude 'sources/' \
  --exclude 'CREDENTIALS.md' \
  ~/phanthy-farm/agents/$SLUG/ \
  /Users/4paradigm/Documents/phanthy/agents/$SLUG/
```

---

## 7. 阶段 1：蒸馏 SOUL

`SOUL.md` 必含 9 节（v2）：

1. 核心语调属性（一句话定位 + 三调性 + 禁忌）
2. 行文习惯与禁忌（标志性句式 5-10 个 + 高频词 + 禁忌）
3. 1500 字扩容策略（**3 步洗稿法**）
4. 标题改造公式
5. 风格自检清单
6. 数据/案例/落地「分层使用纪律」
7. 回复私信风格指南
8. 回复评论风格指南
9. 主动评论 Feed 风格指南

参考模板：`agents/_template/SOUL.md`

---

## 8. 阶段 2：注册资产

| 文件             | 内容                                                                  | 进 git？  |
|------------------|-----------------------------------------------------------------------|-----------|
| `PROFILE.md`     | name / description / 头像 prompt / 预设 3 问 / 备选昵称               | ✅         |
| `BOOT.md`        | 启动指令（路径锁 `<AGENT_ROOT>=~/phanthy-farm/agents/<slug>`）         | ✅         |
| `CREDENTIALS.md` | 模板（`api_key` / `claim_url` 占位），**等 agent 注册后由 agent 自己填** | ❌（gitignore 排除） |

注册流程（OpenClaw 侧）：
1. 用 `PROFILE.md` 的 name/description 调 phanthy `/openclaw/register`
2. 调 gemini-image 生成头像（用 `PROFILE.md` 头像 prompt）
3. 展示给 owner：昵称 + Bio + 头像 + 预设问 + claim_url
4. 等 owner 认领后，把 api_key 写入 `CREDENTIALS.md`

> Codex/Hermes **不**负责注册，只负责产出 PROFILE/BOOT 资产。

---

## 9. 阶段 3：产 Post

每篇 post 必含 **6 文件**：

```
post_XX_<slug>/
├── content.md              # ≥1500 字（3 步洗稿法）
├── manifest.json           # 元数据 + audit.required_files
├── 01_cover.prompt.md      # JSON 模板（封面 prompt）
├── reference.jpg           # 原文封面（img2img 参考图）
├── 02.jpg                  # Top-3 正文图 #1（已裁水印）
├── 03.jpg                  # Top-3 正文图 #2
└── 04.jpg                  # Top-3 正文图 #3
```

### 9.1 content.md 3 步洗稿法（v2）

- **第一步：语料脱水** — 删废话（求点赞/关注/三连/广告/上下篇链接），保留所有干货
- **第二步：骨架映射** — 1:1 平移原文 + 风格平移扩容（补充原理/场景/对比/数据），**每篇洗稿后结构/语气/节奏都不一样**
- **第三步：格式封装** — 末尾强制溯源 `> 💡 深度启发自：[原文标题](原文链接)`

### 9.2 骨架类型（按 agent 内容类型选）

- **A. 月度合集型** — 适合「XX 月新品合集」
- **B. 今日新品型** — 适合「今日新品 | XX + YY」
- **C. 达人专访型** — 适合「实践出针织」「达人作品欣赏」
- **D. 自由型** — 适合科普/教程/观点类（v1 旧规范遗留）

### 9.3 末尾溯源（硬规则）

每篇 content.md 末尾必须有：

```markdown
> 💡 深度启发自：[原文标题](原文链接)
```

### 9.4 4 层标记词 — v2 已废除

v2 不强制 `**观点：**` / `**数据支撑：**` / `**真实案例：**` / `**落地启示：**` 4 层结构。
audit 脚本**不查 4 层标记词**，**只查字数 + 溯源**。

---

## 10. Cover Prompt 规范（v2）

### 10.1 必含字段

```json
{
  "version": "2.0",
  "method": "image_to_image",
  "aspect_ratio": "3:4",
  "reference_image": "reference.jpg",
  "negative_prompt": "blurry, distorted Chinese characters, ...",
  "style": {
    "background": "...",
    "mood": "...",
    "color_grade": "...",
    "lighting": "..."
  },
  "text": {
    "title": {"content": "{TITLE}", ...},
    "subtitle": {"content": "{SUBTITLE}", ...},
    "price_tag": {"content": "{PRICE}", ...}
  },
  "composition": {...},
  "post_generation_check": {...}
}
```

### 10.2 占位符

- `{TITLE}` / `{SUBTITLE}` / `{PRICE}` — 已预填在 01_cover.prompt.md
- agent 上传时直接读 prompt_file 替换占位符

### 10.3 严禁

- **AI 叠中文** — AI 写中文会翻车。AI 出底图，phanthy 平台自动渲染标题。

---

## 11. Manifest Schema

```json
{
  "post_index": "XX",
  "title": "原文标题",
  "source_item_id": "MP_WXS_xxx-item_id",
  "source_orig_url": "https://mp.weixin.qq.com/s/xxx",
  "source_pub_date": "YYYY-MM-DD",
  "agent_slug": "your-slug",
  "content_md": "content.md",
  "cover_text": {
    "title": "封面标题",
    "subtitle": "封面副标题",
    "price": "价格标签"
  },
  "images": [
    {"slot": "reference", "kind": "original", "file": "reference.jpg", "aspect_ratio": 1.0},
    {"slot": "cover", "kind": "ai_prompt", "prompt_file": "01_cover.prompt.md", "method": "image_to_image", "aspect_ratio": 0.75},
    {"slot": "body_1", "kind": "original", "file": "02.jpg", "source_rank": 1, "aspect_ratio": 1.5},
    {"slot": "body_2", "kind": "original", "file": "03.jpg", "source_rank": 2, "aspect_ratio": 1.5},
    {"slot": "body_3", "kind": "original", "file": "04.jpg", "source_rank": 3, "aspect_ratio": 1.5}
  ],
  "phanthy": {
    "tags": ["生活", "娱乐"],
    "sourceUrls": ["原文链接"]
  },
  "audit": {
    "required_files": ["content.md", "01_cover.prompt.md", "reference.jpg", "02.jpg", "03.jpg", "04.jpg"],
    "hard_rule": "缺任一文件即放弃发帖"
  },
  "created_at": "YYYY-MM-DD"
}
```

**phanthy tags 枚举**：小说 / 游戏 / 音乐 / 动漫 / 新闻 / 图像 / 代码 / 视频 / 科普 / 生活 / 娱乐

---

## 12. Audit 规则

### 12.1 硬规则（audit 必须通过）

- 所有 `required_files` 存在
- `content.md` 字数 ≥ 1500（不算标点 `#*>\n\t -|`）
- `content.md` 含「深度启发自」字符串

### 12.2 软规则（warning，不阻塞）

- 4 层标记词（v1 旧规范）— v2 已废除
- 重复图片（warn，agent 自查）
- 边框/水印残留（warn，需人工复核）

### 12.3 跑 audit

```bash
python3 scripts/audit_pending.py --agent-slug X
# 输出 {"total": 5, "ok": 5, "results": [...]}
# exit 0 = 全部 OK
```

---

## 13. Git 协议

### 13.1 必读 .gitignore

仓库已含：

```
**/CREDENTIALS.md
**/sources/raw/
**/sources/*.zip
**/.wemprss_token
.DS_Store
```

### 13.2 禁止进 commit

- ❌ 任何 token / password / api_key
- ❌ 任何 `CREDENTIALS.md` 内容
- ❌ 任何 `sources/raw/` 内容（太大且可重拉）

### 13.3 commit message 格式

```
feat(<agent_slug>): <改动摘要>

<详细说明，1-3 段>
```

### 13.4 push 策略（推荐 HTTPS 一次性 token 注入）

```bash
# 写一个临时 helper（不进 git）
cat > /tmp/cred-helper.sh <<EOF
#!/bin/bash
echo "username=x-access-token"
echo "password=$GITHUB_TOKEN"
EOF
chmod 600 /tmp/cred-helper.sh

# push
git -c credential.helper=/tmp/cred-helper.sh \
    -c credential.useHttpPath=true \
    push https://github.com/TWO-ICE/phanthy-farm.git main

# 清理
rm /tmp/cred-helper.sh
```

> URL 里的 `x-access-token:TOKEN@github.com` 形式 GitHub 已**拒绝**（返回 401）。
> 必须用 credential helper。

### 13.5 push 失败排查

| 错误                                              | 原因                                | 解决                                          |
|---------------------------------------------------|-------------------------------------|-----------------------------------------------|
| `Invalid username or token. Password auth not supported` | URL 形式 `https://TOKEN@github.com` | 用 credential helper                          |
| `Permission denied (publickey)`                    | SSH key 未配                         | 改用 HTTPS                                    |
| `Repository not found`                             | token 缺 `repo` 权限                | 重新签发 PAT with `repo`                      |
| `Could not resolve host`                           | 没走代理                              | `export https_proxy=http://127.0.0.1:7890`    |

---

## 14. Per-Agent 精调机制

### 14.1 覆盖字段

每个 agent 在 `agents/<slug>/AGENT_RULES.md` 顶部用 **YAML front matter** 覆盖 base 字段：

```yaml
---
agent_slug: your-slug
agent_name: 你的博主名
agent_type: 类别           # e.g. crochet_shop / fitness / gossip
article_count: 文章数
status: active | dormant | v1_legacy

image_pipeline:
  top_n_download: 16        # override 12
  min_file_size: 6000       # override 8000
  filter_banner_height: 400

content:
  skeleton: [A, B, C]       # override "free"
  min_chars: 1500
  voice_notes: |
    你的 agent 特有风格描述

cover:
  palette: cream + sage
  forbidden: [neon, plastic]
---
```

### 14.2 读取脚本

```bash
python3 scripts/load_rules.py your-slug
python3 scripts/load_rules.py your-slug --json
```

输出合并后的结构化规则 dict（base + override）。

### 14.3 继承规则

- **完全继承**：base 字段不写 = 走 base 默认
- **深覆盖**：嵌套 dict 逐层合并
- **强制审计**：override 不合法 → load_rules.py 报错

---

## 15. Codex / Hermes 一致性

| 角色         | 干什么                                                                                |
|--------------|---------------------------------------------------------------------------------------|
| **Codex**    | 拉素材 + 蒸馏 SOUL + 产 content.md + manifest + cover prompt + push GitHub              |
| **Hermes**   | 同 Codex，通常在 sandbox 环境跑（erbing 用户），可通过 GITHUB_TOKEN 直接 push          |
| **OpenClaw** | git pull + 注册 phanthy + 心跳（与本仓库解耦）                                          |

**两边必须都 `git pull` 拿最新 AGENT_RULES.md**，**不允许硬编码规则**。

执行时只读：
- `AGENT_RULES.md`（base）
- `agents/<slug>/AGENT_RULES.md`（override）

不读：SOUL.md / PROFILE.md / BOOT.md（在 agent 启动时用，不是 Codex/Hermes 准备内容时用）

---

## 16. 紧急红旗（hermes / codex 立刻停）

- ❌ 任何「是否要 X」问题（除非用户已明确）
- ❌ 任何「如果你想 Y 就告诉我」问题
- ❌ 把 token / password 写进 commit
- ❌ 把 CREDENTIALS.md commit 进 git
- ❌ 改通用规则前不通知（改的是全局）
- ❌ 跳过 pre-flight 的 git pull / 读规则 / 看状态

---

## 17. 已知坑

1. **item/link 不是原文 URL** — 用 `item/guid`
2. **`mmbiz.qpic.cn` 防盗链** — 必须走 wemprss image proxy
3. **URL 里的 `&amp;` 必须解码**才能下载
4. **`watermark=1` 是公众号水印参数**（不是占位图）— fetch_rss 已修
5. **AI 叠不准中文** — AI 出底图，phanthy 平台渲染标题
6. **fetch_rss 默认写 `~/phanthy-farm/`**（不是 template repo）— 写完必须 rsync
7. **wemprss AK/SK 不能用于 REST API** — 用用户名密码 OAuth2
8. **wemprss RSS limit 硬限 30** — 想拉全部用 Tier 2 或 Tier 3
9. **phanthy api_key = agent 身份** — 泄露 = 别人冒充
10. **zsh 的 cwd 问题** — 每次大段命令前先 `cd` 确认
11. **glob 路径 zsh 严格模式失败** — 用 `setopt NULL_GLOB` 或 `ls -d`
12. **git 操作前必须 cd template repo** — `~/phanthy-farm` 改了不自动同步
13. **wemprss OAuth2 401 = 密码错** — 别瞎试（每次扣一次机会）
14. **by_article API 50001** — 从 item_id 解析 mp_id（`MP_WXS_<num>` 格式）
15. **system python3 (3.9.6) 不支持 `str | None` union syntax** — 用 `Optional[str]`
16. **hermes sandbox Python 无 PIL** — 用 `/usr/bin/python3` 跑 PIL 依赖的脚本
17. **GitHub URL 形式 `https://TOKEN@github.com` 401** — 必须用 credential helper
18. **公众号 ID 直接从 URL 反查**（`by_article`），但 50001 时 fallback 到 item_id 解析

---

## 18. 修改本文件的流程

**改通用规则 = 改全局**，慎重：

1. 在 PR 里说明改了什么、为什么
2. 通知所有正在跑的 agent 重新 `git pull`
3. 同步更新 `_template/AGENT_RULES.md`（如有）
4. 考虑回溯修改现有 agent 的 `AGENT_RULES.md`（如改动会破坏现有 agent）
