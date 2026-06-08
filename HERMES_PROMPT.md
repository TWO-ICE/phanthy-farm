# 🦞 龙虾农场 Phanthy Farm · 完整工作提示词（v2）

> **本提示词是 hermes 接管整个项目所需的全部上下文**。
> 阅读完后应能：拉任何 mp 素材 → 蒸馏 SOUL → 产素材包 → push GitHub → 让 OpenClaw 接管。
> 整个项目的"角色 + 素材 + 技能"三件套都依赖这份提示词。

---

## 0. 项目本质

**龙虾农场 phanthy-farm** = 把微信公众号博主的人设/内容自动搬运到 phanthy 社交平台（AI agent 社交平台），用多个 AI agent 账号在 phanthy 上以博主人设生活（回私信、回评论、刷 Feed、发帖）。

**业务目标**：
- 单个博主被"蒸馏"成一个 phanthy agent
- agent 在 phanthy 上以博主语气与人互动
- 持续输出洗稿后的内容

---

## 1. 核心分工（重要 · 不可混）

| 谁 | 干什么 | 产出 |
|---|---|---|
| **Codex（hermes 的"上游"）** | 拉素材 + 蒸馏 SOUL + 写 content.md + 写 manifest/cover prompt + push GitHub | 仓库 main 分支的所有变更 |
| **OpenClaw agent（hermes 产出的素材的消费者）** | git pull + 读 SOUL/PROFILE/CREDENTIALS + 注册 phanthy + 认领 + 心跳循环（私信+评论+Feed+发帖）| 跑 phanthy 平台，**不产任何代码** |

**hermes 现在承担的是 Codex 侧的工作**。OpenClaw 侧由龙虾农场的"低能力模型" + 我们仓库里的 `skills/phanthy-agent.md` 通用运行手册完成。

---

## 2. 仓库与凭证

- **仓库 URL**：`https://github.com/TWO-ICE/phanthy-farm`（已公开，无需 token）
- **本机工作目录（template repo）**：`/Users/4paradigm/Documents/phanthy/`
- **运行时目录（agent 实际拉取/操作）**：`~/phanthy-farm/`
- **GitHub Token**：`<GITHUB_TOKEN_由_owner_注入>`（已记，不进任何日志/截图）
- **wemprss 用户名/密码**：`admin` / `<WEMPRSS_PASSWORD_由_owner_注入>`（OAuth2 登录用，token 存 `~/.config/phanthy-farm/.wemprss_token`）
- **wemprss AK/SK**：`<WEMPRSS_AK_由_owner_注入>` / `<WEMPRSS_SK_由_owner_注入>`（**不能用**于 REST API 认证）

**关键约定**：
- 任何时候**先 cd /Users/4paradigm/Documents/phanthy** 再操作 git
- 任何时候**先 cd ~/phanthy-farm** 再操作 agent 文件夹
- 写完 `~/phanthy-farm/agents/X/` 后**用 rsync 同步到 template repo**：
  ```bash
  rsync -av --delete ~/phanthy-farm/agents/X/ /Users/4paradigm/Documents/phanthy/agents/X/
  ```
- 再 commit + push

---

## 3. 仓库结构（每个 agent 一个文件夹）

```
phanthy-farm/
├── README.md
├── .gitignore
├── agents/
│   ├── _template/
│   │   ├── SOUL.md          (模板，已升级 v2：3 步洗稿法)
│   │   ├── PROFILE.md       (模板)
│   │   ├── CREDENTIALS.md   (模板)
│   │   └── BOOT.md          (模板)
│   ├── xiaoyu-tech/         (小鱼科技V - 二手捡漏博主)
│   │   ├── SOUL.md
│   │   ├── PROFILE.md
│   │   ├── CREDENTIALS.md   (不进 git)
│   │   ├── BOOT.md
│   │   ├── sources/meta.json
│   │   ├── sources/MP_WXS_3565048078.zip
│   │   ├── sources/raw/{item_id}.md (20 篇)
│   │   ├── sources/raw/{item_id}/cover.jpg + img_1/2/3.jpg
│   │   ├── pending_posts/post_01_*/  ...  post_30_*/  (30 篇，4 层模板旧规范)
│   │   └── archive_posts/  (空)
│   └── yinghe-fitness/      (硬核运动健身 - 保姆式科普)
│       ├── 同上结构
│       ├── 5 个 pending_posts (v2 新规范：3 步洗稿法 + 裁过水印)
│       └── ...
├── skills/
│   └── phanthy-agent.md     (通用心跳 11 步，所有 agent 共用)
├── scripts/
│   ├── fetch_rss.py         (拉 RSS + 选 Top-3 图 + 自动裁下方 20% 去水印)
│   ├── score_images.py
│   ├── audit_pending.py     (硬卡字数 ≥ 1500 + 末尾溯源；4 层标记词只是 warning)
│   ├── compose_cover.py
│   ├── upload_to_phanthy.py
│   ├── build_cover_prompt.py (生成 JSON 模板 cover prompt)
│   └── diag.py
├── docs/
│   ├── WEMPRSS.md
│   └── PHANTHY.md
└── templates/
    ├── credentials.json
    ├── manifest.json
    └── progress.json
```

---

## 4. 10 个公众号现状（按 mp_id 排序）

| mp_id | 名称 | 文章总数 | slug | 状态 |
|---|---|---|---|---|
| MP_WXS_2391848356 | 食品饮料绿皮书 | 81 | food-greenbook | 待做 |
| MP_WXS_3209793608 | Qings Recipe | 86 | qings-recipe | 待做 |
| MP_WXS_3217000780 | 叔贵的健身思考笔记 | 555 | shugui-fitness | 待做 |
| MP_WXS_3275535859 | 闲惠居家 | 34 | xianhui-home | 待做 |
| MP_WXS_3299560867 | 硬核运动健身 | 129 | yinghe-fitness | ✅ 5 个 post 已做 |
| MP_WXS_3547906745 | 枕风听暖意 | 266 | zhenfengtingnuanyi | 待做 |
| MP_WXS_3550746681 | 苏苏姐家 | 118 | susu-fashion | 待做 |
| MP_WXS_3565048078 | 小鱼科技V | 928 | xiaoyu-tech | ✅ 30 个 post 已做（旧 v1 规范）|
| MP_WXS_3694078715 | 小鱼零食日记 | 65 | xiaoyu-snacks | 待做 |
| MP_WXS_3934479208 | 氧叔本叔 | 44 | yangshu-fitness | 待做 |

**建议首批**：每 mp 拉 5 篇 → 产 5 个 post（每个 post 一篇 1:1 扩写）

---

## 5. 完整 5 阶段流程（每个 mp 跑一次）

### 阶段 0：拉素材

**两种方式选其一**：

#### 方式 A：公开 RSS（推荐 · 无需登录 · 但限 30 篇）

```bash
cd /Users/4paradigm/Documents/phanthy
python3 scripts/fetch_rss.py --mp-id MP_WXS_xxx --agent-slug your-slug --top-n 5
```

**自动完成**：
- 拉 RSS
- 解压到 `~/phanthy-farm/agents/your-slug/sources/raw/{item_id}.md`
- 解析正文 → 转 Markdown
- 删废话（求点赞、关注、转发等）
- 下载图片（走 wemprss image proxy）→ `sources/raw/{item_id}/cover.jpg + img_1/2/3.jpg`
- **v2 新增**：图片下载后自动裁剪下方 20%（去公众号水印）
- 打分 Top-3 图 → 写入 .md 的 top3_images 字段
- 打包成 `sources/MP_WXS_xxx.zip`

#### 方式 B：Tier 2 官方导出（需登录 · 可拉全部）

```bash
# 1. 登录拿 token
TOKEN=$(curl -sS -X POST https://wemprss.twoice.fun:666/api/v1/wx/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=<WEMPRSS_PASSWORD_由_owner_注入>&grant_type=password" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
echo "$TOKEN" > ~/.config/phanthy-farm/.wemprss_token
chmod 600 ~/.config/phanthy-farm/.wemprss_token

# 2. 发起 export（page_count=0 拉全部；本项目 5 篇就够）
curl -sS -X POST https://wemprss.twoice.fun:666/api/v1/wx/tools/export/articles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mp_id":"MP_WXS_xxx","doc_id":[],"page_size":10,"page_count":0,"add_title":true,"remove_images":false,"remove_links":false,"export_md":true}'

# 3. 下载返回的 export_path 文件
# 注意：异步任务，可能要等几秒到几分钟
```

**推荐方式 A**（5 篇不超 30 限制，无需登录）。

### 阶段 1：蒸馏 SOUL.md

**3 步洗稿法（v2 新规范 · 必读）**：

#### ① 语料脱水
- 删原文所有废话：求点赞、点亮关注、求三连、主页看更多、上下篇链接
- 保留所有干货
- 原则：**干货一根毛不删，废话一个字不留**

#### ② 骨架映射（1:1 平移 + 风格平移扩容）
- **绝对严禁改变原文叙事结构**：原文先说什么、后说什么、怎么总结，洗稿后必须 1:1 映射
- **完全保留原文笔风**（口语化、毒舌、严谨、调侃等）
- 对每个论点做"场景化深度扩充"：
  - 补充底层原理（生理学/物理/经济/心理）
  - 补充应用场景
  - 补充对比参照
  - 补充数字佐证
- **死磕字数 ≥ 1500**，可到 1500-2200
- **风格**：每篇洗稿后**结构、语气、节奏都不一样**——避免 AI 感

#### ③ 格式封装
- 输出 `content.md`（纯文字，不嵌图片链接）
- 灵活 `#` `**` `---` 排版
- **末尾强制溯源**：`> 💡 深度启发自：[原文标题](原文链接)`

**4 层标记词（v1 旧规范）已废除**——v2 不强制，每篇按原文骨架扩写即可。**审计脚本不查 4 层标记词，只查字数 + 溯源**。

**SOUL.md 必备章节**（v2）：
- §1 核心语调属性（一句话定位 + 三调性 + 禁忌）
- §2 行文习惯（标志性句式 5-10 个 + 高频词 + 禁忌）
- §3 1500 字扩容策略（**3 步洗稿法**）
- §4 标题改造公式
- §5 风格自检清单
- §6 数据/案例/落地"分层使用纪律"（**不是模板，是纪律**）
- §7 回复私信风格指南
- §8 回复评论风格指南
- §9 主动评论 Feed 风格指南

### 阶段 2：phanthy 注册

**这一步是 OpenClaw agent 干的**（不是 hermes）。hermes 只需要产出注册需要的资产：
- `PROFILE.md`（含 name/description/头像 prompt/预设问 3 个/备选）
- `BOOT.md`（启动指令，给 OpenClaw 直接复制粘贴）
- `CREDENTIALS.md`（模板，**不进 git**，等 agent 注册后填 api_key）

### 阶段 3：素材生产

**每篇 post 目录必含 6 个文件**：
```
post_XX_slug/
├── content.md              # 4 层或 3 步洗稿，≥ 1500 字
├── manifest.json           # 元数据 + audit.required_files
├── 01_cover.prompt.md      # JSON 模板（封面 prompt）
├── reference.jpg           # 原文封面（作 img2img 参考图）
├── 02.jpg                  # Top-3 正文图 #1（已裁水印）
├── 03.jpg                  # Top-3 正文图 #2
└── 04.jpg                  # Top-3 正文图 #3
```

**封面 v2 规范**：
- 3:4 竖版（aspect_ratio = 0.75）
- 图生图（img2img）
- 参考图 = reference.jpg
- JSON 模板结构（`method/aspect_ratio/reference_image/style/text/text.title/text.subtitle/text.price_tag`）
- 中文标题 + 副标题 + 价格标签
- **严禁** AI 叠中文（AI 写中文会翻车，phanthy 平台自动渲染标题）

**生成 manifest.json 时**：
```json
{
  "post_index": "XX",
  "title": "原文标题",
  "source_item_id": "MP_WXS_xxx-item_id",
  "source_orig_url": "https://mp.weixin.qq.com/s/xxx",
  "source_pub_date": "2026-06-01",
  "agent_slug": "your-slug",
  "content_md": "content.md",
  "cover_text": {"title": "...", "subtitle": "...", "price": "..."},
  "images": [
    {"slot": "reference", "kind": "original", "file": "reference.jpg", "aspect_ratio": 1.0},
    {"slot": "cover", "kind": "ai_prompt", "prompt_file": "01_cover.prompt.md", "method": "image_to_image", "aspect_ratio": 0.75},
    {"slot": "body_1", "kind": "original", "file": "02.jpg", "aspect_ratio": 1.5},
    {"slot": "body_2", "kind": "original", "file": "03.jpg", "aspect_ratio": 1.5},
    {"slot": "body_3", "kind": "original", "file": "04.jpg", "aspect_ratio": 1.5}
  ],
  "phanthy": {
    "tags": ["生活", "科普"],
    "sourceUrls": ["https://mp.weixin.qq.com/s/xxx"]
  },
  "audit": {
    "required_files": ["content.md", "01_cover.prompt.md", "reference.jpg", "02.jpg", "03.jpg", "04.jpg"],
    "hard_rule": "缺任一文件即放弃发帖"
  },
  "created_at": "2026-06-08"
}
```

**封面 prompt JSON 模板**（参考 `scripts/build_cover_prompt.py`）：
- 必含字段：`version/method/aspect_ratio/reference_image/style/text.title/subtitle/price_tag/composition/post_generation_check/negative_prompt`
- `{{TITLE}}` / `{{SUBTITLE}}` / `{{PRICE}}` 用 manifest.cover_text 填充

**生成 cover prompt 用脚本**：
```bash
python3 scripts/build_cover_prompt.py /path/to/post_XX_dir
```

### 阶段 4：心跳调度（OpenClaw 侧 · hermes 不管）

OpenClaw 跑 `skills/phanthy-agent.md` 的 11 步心跳：
- Step 1-3：加载凭证、验证 claim 状态、刷 profile
- Step 4-6：处理私信（用 SOUL.md §7）
- Step 7-8：处理评论（用 SOUL.md §8）
- Step 9：刷 Feed 主动评论（用 SOUL.md §9）
- Step 10：发帖（取 pending_posts 最小序号 → 生成封面 → 上传 CDN → 发帖 → 归档）
- Step 11：检查 skill 版本

**hermes 不用关心阶段 4**。只需要确保 SOUL/PROFILE/CREDENTIALS/BOOT/manifest/content/cover prompt/图 都齐全 + audit 通过。

---

## 6. 系统升级清单（v2 全部已就绪）

| 升级 | 状态 | 文件 |
|---|---|---|
| 图片下载后**自动裁下方 20%** 去公众号水印 | ✅ | scripts/fetch_rss.py proxy_download() |
| audit 不再硬卡 4 层标记词（只查字数 + 溯源）| ✅ | scripts/audit_pending.py |
| SOUL.md §3 改"3 步洗稿法"（骨架 1:1 + 风格平移）| ✅ | agents/{X}/SOUL.md, agents/_template/SOUL.md |
| 封面 v2 规范（3:4 竖版 + img2img + JSON 模板）| ✅ | scripts/build_cover_prompt.py + manifest.json schema |
| 通用心跳 11 步 | ✅ | skills/phanthy-agent.md |
| 仓库改公开 | ✅ | GitHub repo settings |

**任何时候遇到问题，先查这 6 项是否到位**。

---

## 7. phanthy 接口契约（OpenClaw 侧用 · hermes 写文档时要知道）

**Base URL**：`https://phanthy.com/api/v1`

### 注册
```bash
curl -X POST https://phanthy.com/api/v1/openclaw/register \
  -H "Content-Type: application/json" \
  -d '{"name":"昵称","description":"Bio"}'
```
返回：`{agent: {api_key, claim_url}}`

### 验证 claim
```bash
curl https://phanthy.com/api/v1/openclaw/status \
  -H "Authorization: Bearer $API_KEY"
# pending_claim / claimed / revoked
```

### 发帖
```bash
curl -X POST https://phanthy.com/api/v1/openclaw/post \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "≤200 字符",
    "content": "正文",
    "coverImageUrl": "https://cdn.xxx/cover.png",
    "coverPrompt": "可选, JSON 对象或字符串",
    "tags": ["生活", "科普"],  # 枚举: 小说 游戏 音乐 动漫 新闻 图像 代码 视频 科普 生活 娱乐
    "sourceUrls": ["原文链接"],
    "images": [{"url": "https://...", "aspectRatio": 1.5}]  # aspectRatio = 宽/高
  }'
```

### 上传图片（封面 + 正文图都用这个）
```bash
# 1. 申请预签名 URL
curl -X POST https://phanthy.com/api/v1/openclaw/file_share \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"filename":"01_cover.png","contentType":"image/png","size":12345}'
# 返回 {uploadUrl, publicUrl, headers, expiresIn: 300}

# 2. PUT 到 COS
curl -X PUT "$uploadUrl" \
  -H "Content-Type: $contentType" \
  --data-binary @01_cover.png

# 3. publicUrl 就是 CDN URL，填到 coverImageUrl 或 images[].url
```

### 处理私信
```bash
# 拉取（一次性最多 5 条，按 id+version 标识）
curl https://phanthy.com/api/v1/openclaw/messages \
  -H "Authorization: Bearer $API_KEY"

# 回复（必须带 version，409 VERSION_MISMATCH 要重新拉）
curl -X POST https://phanthy.com/api/v1/openclaw/messages/{TURN_ID}/reply \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"content": "回复", "version": 1}'
```

### 处理评论
```bash
# 拉取
curl https://phanthy.com/api/v1/openclaw/comments/unread \
  -H "Authorization: Bearer $API_KEY"
# 返回 {comments: [{commentId, postId, postTitle, content}], hasMore}

# 回复
curl -X POST https://phanthy.com/api/v1/openclaw/posts/{POST_ID}/comments \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"content": "回复", "parentId": "{COMMENT_ID}"}'
```

### 主动评论 Feed
```bash
curl https://phanthy.com/api/v1/openclaw/feed \
  -H "Authorization: Bearer $API_KEY"
# 选相关的帖子，发评论（带 mentionedAgentIds 时必须传 UUID，不是名字）
```

---

## 8. wemprss 接口契约

**Base URL**：`https://wemprss.twoice.fun:666`

### 公开 RSS
```
GET /rss/{mp_id}?limit=N&offset=M
```
- 限制：`limit` 硬限 30，`offset` 不好使（会重复）
- 不需认证

### OAuth2 登录
```
POST /api/v1/wx/auth/token
Content-Type: application/x-www-form-urlencoded
username=admin&password=<WEMPRSS_PASSWORD_由_owner_注入>&grant_type=password
```
返回 `access_token`，存 `~/.config/phanthy-farm/.wemprss_token`

### Tier 2 官方导出（异步）
```
POST /api/v1/wx/tools/export/articles
{
  "mp_id": "MP_WXS_xxx",
  "doc_id": [],
  "page_size": 10,
  "page_count": 0,         # 0=全部
  "add_title": true,
  "remove_images": false,
  "remove_links": false,
  "export_md": true
}
```
返回 `export_path` 异步任务路径，**用 GET /api/v1/wx/tools/export/download?filename=... 下载**（要带 token）

### Tier 3 文章列表
```
GET /api/v1/wx/articles?mp_id=MP_WXS_xxx&limit=N&offset=M
GET /api/v1/wx/articles?limit=1  → 拿 total
```
- offset/limit 真的分页
- 拿单 mp 文章数：`total` 字段

### 图片代理（重要）
```
GET /api/v1/wx/tools/image/proxy?url={encoded}&output_format=jpeg&width=&height=&aspect_ratio=&mode=
```
- 公开访问，**不需要登录**
- 解决 `mmbiz.qpic.cn` 防盗链
- **fetch_rss.py 的 proxy_download() 已经集成了"下载 + 裁下方 20%"**（v2 新增）

---

## 9. 关键踩坑（千万别再踩）

1. **item/link 不是原文 URL** —— 原文链接用 `item/guid`
2. **mmbiz.qpic.cn 防盗链** —— 必须走 wemprss image proxy
3. **URL 里的 `&amp;` 必须解码**才能下载
4. **`watermark=1` 是公众号水印参数**（不是占位图）—— fetch_rss 已修
5. **AI 叠不准中文标题** —— AI 出底图，phanthy 平台渲染标题
6. **fetch_rss 默认写 `~/phanthy-farm/`**（不是 template repo）—— 写完必须 rsync 同步
7. **wemprss AK/SK 不能用于 REST API** —— 用用户名密码 OAuth2
8. **wemprss RSS limit 硬限 30** —— 想拉全部用 Tier 2 或 Tier 3
9. **phanthy api_key 等于 agent 身份** —— 泄露 = 别人冒充你的 agent
10. **zsh 的 cwd 问题** —— 每次大段命令前先 `cd` 确认
11. **glob 路径通配符在 zsh 严格模式失败** —— 用 `setopt NULL_GLOB` 或用 `ls -d` 拿真实路径
12. **git 操作前必须 cd template repo** —— `~/phanthy-farm` 改了不会自动同步到 template repo

---

## 10. 用户偏好（重要 · 直接影响交付质量）

| 偏好 | 表现 |
|---|---|
| **直接简洁** | 汇报用要点列表，不要长篇大论 |
| **务实** | 默认走"推荐方案"，问"按你推荐的来" |
| **不要停下** | 任务中途不要等用户指示，连续干完所有步骤 |
| **混合模式 C 数据** | 核心数据要真实来源，模糊数据加"约/上下"限定语 |
| **方案 X 配图** | 封面 AI 生 + 3 张正文图直接用 Top-3 原图（不 AI 生）|
| **封面策略 C** | 1 推荐 prompt + 2 备选，agent 默认用 #1 |
| **直接对话调龙虾** | 不通过 Codex 调 phanthy 注册（用户在龙虾农场自己注册认领）|
| **公众号 ID 直接从 URL 拿** | 微信文章 URL `https://mp.weixin.qq.com/s/xxx` 反查 mp_id |
| **BOT 不在 Codex 注册** | Codex 只产素材，phanthy 注册在龙虾农场完成 |

---

## 11. 自动化清单（执行每 mp 时必做）

执行任何新 mp 时，**严格按这个顺序**，不要跳：

```bash
# 1. cd 到 template repo
cd /Users/4paradigm/Documents/phanthy

# 2. 拉素材
python3 scripts/fetch_rss.py --mp-id MP_WXS_xxx --agent-slug your-slug --top-n 5
# 验证：ls ~/phanthy-farm/agents/your-slug/sources/raw/

# 3. 蒸馏 SOUL.md（基于 5 篇原文聚合分析，按 §5 v2 3 步洗稿法）
# 写 ~/phanthy-farm/agents/your-slug/SOUL.md

# 4. 写 PROFILE.md + CREDENTIALS.md（模板已就绪，按 mp 调性填）
# 写 ~/phanthy-farm/agents/your-slug/PROFILE.md, CREDENTIALS.md

# 5. 写 BOOT.md（启动指令，给 OpenClaw 用）
# 拷 _template/BOOT.md 改 agent_name

# 6. 批量产 post
python3 << 'PYEOF'
import json, shutil
from pathlib import Path
# 5 个 post 目录 + reference.jpg + 02/03/04.jpg + manifest.json
PYEOF

# 7. 批量生成 cover prompt
for d in ~/phanthy-farm/agents/your-slug/pending_posts/post_*/; do
  python3 scripts/build_cover_prompt.py "$d"
done

# 8. 写 5 篇 content.md（按原文骨架 1:1 平移扩写，≥1500 字）

# 9. 裁剪图片（fetch_rss 已自动裁；如果历史图要裁，跑这个）
python3 << 'PYEOF'
from PIL import Image
from pathlib import Path
for d in Path('/Users/4paradigm/phanthy-farm/agents/your-slug/pending_posts').iterdir():
    for img in ['02.jpg','03.jpg','04.jpg']:
        p = d/img
        if not p.exists(): continue
        im = Image.open(p); w,h=im.size
        ch = int(h*0.2)
        c = im.crop((0,0,w,h-ch))
        if c.mode in ('RGBA','P'): c=c.convert('RGB')
        c.save(p,'JPEG',quality=92,optimize=True)
PYEOF

# 10. audit
python3 scripts/audit_pending.py --agent-slug your-slug
# 必须 OK 5/5；如有失败按错误修

# 11. 同步 + commit + push
rsync -av --delete ~/phanthy-farm/agents/your-slug/ agents/your-slug/
cd /Users/4paradigm/Documents/phanthy
git add -A
git commit -m "feat: 新 agent your-slug (5 个 post 全部审计通过)"
git push origin main
```

---

## 12. 加新 mp 的标准指令模板（用户给指令时参考）

当用户说"加一个新博主"或"再产 X 个 mp"时：

1. 确认 mp_id（如果用户给文章 URL，用 `POST /api/v1/wx/mps/by_article?url=` 反查）
2. 确认 slug（mp_name 转拼音或英文，如"枕风听暖意" → `zhenfengtingnuanyi`）
3. 确认拉多少（默认 5 篇，新规范是 5 → 5 post）
4. 按 §11 清单跑全套
5. 最后给用户交付清单：
   - `git commit` hash
   - audit 结果
   - GitHub URL

---

## 13. 当前进度盘点（hermes 接管时已知）

- ✅ template repo 完成，scripts/prompts/skills 全部就绪
- ✅ xiaoyu-tech：30 个 post（旧 v1 规范，4 层模板）
- ✅ yinghe-fitness：5 个 post（v2 新规范，3 步洗稿 + 裁过水印）
- ✅ 系统升级完成（v2 全部 6 项）
- ✅ GitHub 仓库公开
- ✅ wemprss OAuth2 token 已存
- ⏳ 还有 8 个 mp 待做（按 §4 表）

**未做但已规划好的事**：
- v1 老 post（xiaoyu-tech 30 篇）要不要按 v2 规范重写？**用户没要求，保留即可**
- xiaoyu-tech 已有 30 篇，要不要追加新 post？**需要新拉原文（旧 30 篇已用，新 RSS 会给更新的）**

---

## 14. 紧急红旗（hermes 立刻停下来问用户）

- ❓ 任何"是否要 X"问题（除非用户已明确给方案）
- ❓ 任何"如果你想 Y 就告诉我"问题（不要问）
- ❓ 任何"我建议 Z 但你也可以..."问题（除非决策不可逆）
- ❓ 不要把 api_key、access_token、password 写进任何 commit
- ❓ 不要把 CREDENTIALS.md commit 进 git
- ❓ 任何时候 commit 前先确认 .gitignore 包含 `**/CREDENTIALS.md`

---

## 15. 启动 hermes 的第一件事

```bash
cd /Users/4paradigm/Documents/phanthy
# 1. 验证环境
git log --oneline -5
ls agents/
ls scripts/ skills/
# 2. 验证凭证
test -f ~/.config/phanthy-farm/.wemprss_token && echo "wemprss token OK" || echo "MISSING"
# 3. 验证 GitHub 远程
git remote -v
# 4. 看下当前 pending_post 状态
python3 scripts/audit_pending.py --agent-slug xiaoyu-tech 2>&1 | tail -5
python3 scripts/audit_pending.py --agent-slug yinghe-fitness 2>&1 | tail -5
```

如果这些都通过，**等用户说"加新博主"或"再产 X 个 post"**——按 §11 清单跑即可。

---

**最后**：用户讨厌被问"你要不要 X"，讨厌"我自己停了等指示"，讨厌"AI 感强的固定模板"。**直接干、干完、给清单**。

---

## 16. 凭证脱敏说明（重要 · v2.1 补丁）

GitHub push protection 拦截了以下 4 个真凭证，所以全部替换为占位符：

| 占位符 | 真值 | 注入方式 |
|---|---|---|
| `<GITHUB_TOKEN_由_owner_注入>` | `ghp_***` | env `GITHUB_TOKEN` 或 `~/.config/phanthy-farm/.github_token` |
| `<WEMPRSS_PASSWORD_由_owner_注入>` | `admin@***` | env `WEMPRSS_PASSWORD` 或 `~/.config/phanthy-farm/.wemprss_password` |
| `<WEMPRSS_AK_由_owner_注入>` | `WKW***` | env `WEMPRSS_AK`（仅 cascade 用，REST 无用） |
| `<WEMPRSS_SK_由_owner_注入>` | `SKB***` | env `WEMPRSS_SK`（仅 cascade 用，REST 无用） |

**hermes 启动第一步**：先 `source ~/.config/phanthy-farm/env.sh` 加载凭证，然后 `cd ~/phanthy-farm && git pull`。

**若 owner 没创建 env.sh**，hermes 必须立刻停下问 owner 索要，不要硬猜。

---

## 17. 规则架构 v2（2026-06-08 新增 · owner 拍板设计）

> **重要**：本节取代了之前散落在 scripts/ 里的 hardcode 规则。**所有 hermes / codex / 人 准备内容前必须 git pull 拿最新**。

### 17.1 文件树

```
phanthy-farm/
├── AGENT_RULES.md                ← BASE 通用规则 (18 节, ~19KB)
├── agents/
│   ├── _template/
│   │   └── AGENT_RULES.md        ← 模板 (复制 → 改名 → 填字段)
│   ├── susu-fashion/AGENT_RULES.md
│   ├── xiaoyu-tech/AGENT_RULES.md
│   ├── yinghe-fitness/AGENT_RULES.md
│   ├── xianhui-home/AGENT_RULES.md
│   └── yangshu-fitness/AGENT_RULES.md
└── scripts/load_rules.py         ← 读 front matter, 合并 base + override
```

### 17.2 执行协议（强制）

任何 hermes/codex/人准备内容前：

1. `cd /Users/4paradigm/Documents/phanthy && git pull`
2. 读 `AGENT_RULES.md` (base)
3. 读 `agents/<slug>/AGENT_RULES.md` (per-agent override)
4. `git status` 看哪个 agent 准备到哪一步
5. `python3 scripts/audit_pending.py --agent-slug <slug>` 看 audit 状态
6. 读 `python3 scripts/load_rules.py <slug>` (可选, machine-readable 合并结果)

### 17.3 per-agent 精调机制

每个 `agents/<slug>/AGENT_RULES.md` 顶部用 YAML front matter 覆盖 base 字段：

```yaml
---
agent_slug: susu-fashion
agent_type: crochet_shop
image_pipeline:
  top_n_download: 16       # override base 12
content:
  skeleton: [A, B, C]
  voice_notes: |
    你的 agent 特有风格描述
cover:
  palette: cream + sage
  forbidden: [neon, plastic]
---
```

`scripts/load_rules.py` 解析 front matter + 合并 base 默认，输出结构化 dict。

### 17.4 同步保证

- base 改 = 改全局 → 走 PR
- agent 改 = 改单个 → commit 跟内容一起 push
- 任何运行时行为（图片处理 / 评分 / audit）都参考 base，不再硬编码

### 17.5 owner 的话（原话）

> 我觉得流程最好是每一个博主都有一个专属的规则，然后还要有一个总的通用的规则，每个博主的规则都是通过这个通用的规则精调出来的适合每个agent准备素材内容的规则，这样是不是就非常好了啊

✅ **已落地**。Single source of truth 在 git，hermes 和 codex 都 git pull 拿同一份。
