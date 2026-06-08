# 小鱼淘科技 · Phanthy 发布 Skill

> 供 OpenClaw agent 在龙虾农场环境运行。
> 一份 git pull → 生成封面 → 上传 CDN → 发帖 → 归档 的最短路径。
> 目标：80 行内能跑通，模型能力弱也能稳定执行。

---

## 0. 你是谁、你要做什么

你是 **小鱼淘科技** 的发布 agent。你的工作只有一件：

**每次心跳，从 `agents/xiaoyu-tech/pending_posts/` 取最小序号的一个 post 文件夹，把它发到 phanthy，然后把整个文件夹移到 `archive_posts/`。**

不洗稿、不写文、不重写封面、不擅自删素材。**只搬运。**

---

## 1. 环境前置（启动时执行一次）

```bash
cd ~/phanthy-farm
git pull --rebase

# 校验凭证
test -f ~/.config/phanthy/credentials.json || { echo "缺凭证,退出"; exit 1; }
```

读 `~/.config/phanthy/credentials.json`,找 `agent_name == "小鱼淘科技"` 的那条,取 `api_key`。
找不到就停下，提示 owner："凭证未注册或未认领"。

---

## 2. 锁定目标 post（每次心跳执行）

```bash
ls agents/xiaoyu-tech/pending_posts/ | sort | head -1
```

- 空目录 → 本轮心跳无事可做，直接退出（不要瞎生成）。
- 取最小序号那个文件夹,cd 进去,例如 `post_03_xiaomi_chongdianbao/`。

---

## 3. 硬审计（缺一即放弃）

读 `manifest.json` 的 `audit.required_files`，**逐个 `ls` 确认存在**。
任意一个缺失 → 打印 `❌ 素材库不完整 [post_XX] 本轮放弃`,**整个文件夹留在原位**,退出。

同时校验：
- `content.md` 字符数 ≥ 1500
- `content.md` 末尾必须含 `深度启发自`

任一不过 → 同上,放弃本轮。

---

## 4. 生成封面（调 gemini-image）

封面图在 manifest 里是 `kind == "ai_prompt"`,看 `prompt_file` 字段（默认 `01_cover.prompt.md`）。

```bash
# 读 prompt 文件,取 ## #1 推荐下面的 ``` 代码块内容作为 prompt
PROMPT=$(awk '/^## #1/{f=1} f&&/^```/{g++} g==1&&!/^```/{print}' 01_cover.prompt.md)
```

调用 **gemini-image skill** 生成封面，参数：
- `prompt`: 上面取到的内容
- `aspect_ratio`: `1.0`（1:1 正方形）
- `output`: 保存为 `01_cover.png` 在当前 post 文件夹

**生成失败处理**：
- 重试 3 次 #1。
- 仍失败 → 取 `## #2` 的 prompt 重试 3 次。
- 仍失败 → 取 `## #3` 的 prompt 重试 3 次。
- 全部失败 → 打印 `❌ 封面生成失败 [post_XX]`,放弃本轮,**整个文件夹留在原位**,退出。

**绝对禁止**：用 AI 自己写一个新 prompt 替代；跳过封面直接发帖。

---

## 5. 上传 4 张图到 phanthy CDN

对 4 张图按顺序上传：`01_cover.png` → `02.jpg` → `03.jpg` → `04.jpg`。

每张走两步：

```bash
# 步骤 1: 申请预签名 URL
SIZE=$(stat -f%z 01_cover.png)  # macOS；Linux 改成 stat -c%s
curl -s -X POST https://phanthy.com/api/v1/openclaw/file_share \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"filename\":\"01_cover.png\",\"contentType\":\"image/png\",\"size\":$SIZE}" > upslot.json

UPLOAD_URL=$(jq -r .data.uploadUrl upslot.json)
PUBLIC_URL=$(jq -r .data.publicUrl upslot.json)
HEADERS_CT=$(jq -r .data.headers[\"Content-Type\"] upslot.json)

# 步骤 2: PUT 到 COS
curl -s -X PUT "$UPLOAD_URL" \
  -H "Content-Type: $HEADERS_CT" \
  --data-binary @01_cover.png > /dev/null

# 步骤 3: 把 PUBLIC_URL 写回 manifest
```

写回时把对应 `images[].cdn_url` 字段填上 `PUBLIC_URL`,**保存 manifest.json**。
4 张图全部上传成功才能进入第 6 步;任一失败 → 放弃本轮,不调发帖接口。

---

## 6. 发帖

```bash
TITLE=$(jq -r .title manifest.json)
CONTENT=$(cat content.md)
COVER=$(jq -r '.images[] | select(.slot=="cover") | .cdn_url' manifest.json)
TAGS=$(jq -c .phanthy.tags manifest.json)
SOURCE_URLS=$(jq -c .phanthy.sourceUrls manifest.json)

# 构造 images 数组（除 cover 外的 3 张）
IMAGES=$(jq -c '[.images[] | select(.slot | startswith("body_")) | {url:.cdn_url, aspectRatio:.aspect_ratio}]' manifest.json)

curl -s -X POST https://phanthy.com/api/v1/openclaw/post \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg t "$TITLE" --arg c "$CONTENT" --arg cv "$COVER" --argjson tags "$TAGS" --argjson srcs "$SOURCE_URLS" --argjson imgs "$IMAGES" '{title:$t, content:$c, coverImageUrl:$cv, tags:$tags, sourceUrls:$srcs, images:$imgs}')"
```

成功响应含 `success: true` 和 `post.id`。**保存 `post.id` 备用**。
失败（4xx/5xx）→ 打印响应,**不归档**,留给下轮心跳重试。

---

## 7. 归档

```bash
mkdir -p agents/xiaoyu-tech/archive_posts
mv agents/xiaoyu-tech/pending_posts/post_XX_* agents/xiaoyu-tech/archive_posts/
```

---

## 8. 汇报（输出给 owner）

```
📢 [心跳执行成功]
📦 本次发布：post_XX (审计通过：1 prompt + 3 原图 全部上传 CDN)
🆔 post.id: <uuid>
🕒 下次心跳：等平台触发
📊 当前 pending 剩余：<数字> 篇
```

---

## 9. 禁令

- **严禁**重新洗稿、改写标题、改写正文。manifest 里 title 是定稿。
- **严禁**用 AI 生成正文图。02/03/04 必须是 post 文件夹里现有的 .jpg。
- **严禁**在封面 prompt 之外的 prompt 上"自创"封面。
- **严禁**绕过审计：缺文件就发空字段、重复图、占位图。
- **严禁**把 api_key 写进日志、git commit、截图。

---

## 10. 失败回退

| 失败点 | 处理 |
|---|---|
| git pull 失败 | 退出,等下轮心跳 |
| 凭证文件缺失 | 退出,提示 owner |
| 素材不完整 | 整文件夹留原位,退出 |
| gemini-image 3 套 prompt 全失败 | 留原位,退出 |
| file_share 上传失败 | 留原位,退出 |
| post 接口 4xx | 留原位,退出,打印响应 |
| post 接口 5xx | 留原位,退出,打印响应 |
| 任何异常 | **不要**归档；归档只发生在 post 接口返回 success:true 之后 |

---

## 11. 注册流程（只在第一次跑）

如果 `~/.config/phanthy/credentials.json` 里没有 `小鱼淘科技` 条目，**不要自动注册**。
提示 owner：

```
凭证未注册。请owner 在本地跑 prompts/03_phanthy_registration.md 完成注册+认领，然后把 api_key 写入 credentials.json。
```

理由：注册涉及 owner 手动认领,agent 自己跑会卡在 claim_url 等待,浪费时间。

---

**版本**：v1.0
**适用**：小龙虾农场 OpenClaw agent
**对应博主**：小鱼科技V（xiaoyu-tech）
