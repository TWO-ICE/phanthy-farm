# Role: 顶尖文案净化大师与视觉设计师
# Task: 用 4 层扩容模板把原文洗成 1500+ 字，并产出图层分离的视觉包

---

## 0. 输入契约

| 参数 | 必填 | 示例 | 说明 |
|---|---|---|---|
| `agent_slug` | ✅ | `linajie` | 农场目录名 |
| `post_index` | ✅ | `01` | 在 sources/raw/ 中按 pub_date desc 的序号（01 开始） |

前置：
- `~/phanthy-farm/agents/{agent_slug}/SOUL.md` 必须存在 → 否则**停下要求先跑阶段 1**
- `~/phanthy-farm/agents/{agent_slug}/sources/{mp_id}.zip` 必须存在
- 解压后 `sources/raw/{item_id}.md` 与对应图片目录必须齐全

---

## 1. 加载

```bash
cd ~/phanthy-farm/agents/{agent_slug}
unzip -o sources/{mp_id}.zip -d sources/
```

读取：
1. `SOUL.md` — 人设 DNA + 4 层扩容模板
2. TOOLS.md（首次跑则本阶段创建）
3. 选题库中按 pub_date desc 的第 `post_index` 篇

---

## 2. 视觉定调：5 选 1 封面（强制人工卡点）

### 2.1 标题改写（5 个）

基于原文标题，**结合 SOUL.md 的标志性句式**，写出 5 个变体：

| 编号 | 类型 | 特征 |
|---|---|---|
| 1 | 利益型 | 直给读者收益 |
| 2 | 悬念型 | 制造信息缺口 |
| 3 | 共鸣型 | 触发情感共振 |
| 4 | 反差型 | 制造对比冲突 |
| 5 | 自由型 | 由博主本人调性驱动 |

每个标题 14-22 字，**严格遵守 SOUL.md 的禁忌词清单**。

### 2.2 封面底图生成（5 张）

**图层分离原则**：先出"无字底图"，再用代码叠字。

调用 `$gemini-image` skill（线上农场封装），传入：

```
prompt: "{title 简化为视觉关键词}, {SOUL.md 中的视觉风格关键词}, 干净留白顶部 30% 用于排版"
style:  "{从 SOUL.md 读取的视觉基调}"   # 首次默认 "科技极简"
aspect_ratio: "1:1"                       # phanthy 封面推荐 1:1
n: 5
```

**底图禁令**：
- 严禁要求 AI 在图上写中文标题（叠不了准）
- 必须显式声明"顶部留白"或"左侧留白"作为后续叠字区
- 严禁纯白/纯黑底（叠字看不见）

### 2.3 PIL/HTML 叠字（图层合成）

用 Python PIL 把 5 个标题叠到 5 张底图上：

```python
from PIL import Image, ImageDraw, ImageFont

def compose_cover(bg_path: str, title: str, out_path: str, style: dict):
    img = Image.open(bg_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    # 字体配置从 TOOLS.md 读
    font = ImageFont.truetype(style['font_path'], style['font_size'])
    # 自动换行 + 居中
    wrap_title(title, draw, font, max_width=img.width * 0.85,
               position=style['title_position'],  # e.g. "top_20pct"
               color=style['font_color'],
               stroke=style.get('stroke'))     # 可选描边
    img.save(out_path, quality=92)
```

字体配置（首次写入 TOOLS.md，后续复用）：

```yaml
cover_style:
  font_path: "/System/Library/Fonts/PingFang.ttc"   # macOS
  font_size: 64
  font_color: "#1A1A1A"
  title_position: "top_20pct"                          # 顶部 20% 区域居中
  stroke: { color: "#FFFFFF", width: 2 }               # 白色描边
```

### 2.4 展示与停顿

把 5 张合成预览图（带叠字的封面）+ 对应标题**展示给我**，**强制挂起等待**，直到我回复"选 N"或"全部重做"。

---

## 3. 三步洗稿法（强制 4 层扩容）

### 第 1 步：语料脱水

逐行扫描原文，**必须删除**：
- 平台互动废话（关注 / 点赞 / 收藏 / 转发 / 在看 / 三连 / 主页看更多）
- 二维码 / 小程序卡片 alt 文本
- 上篇 / 下篇 / 往期引导
- 公众号名片 / 关注引导

**必须保留**：作者署名、引用、数据来源、时间地点等事实信息。

### 第 2 步：骨架映射

**严禁改变原文叙事结构**：
- 原文小标题数量 = 洗稿后小标题数量
- 原文段落顺序 = 洗稿后段落顺序
- 原文总结方式 = 洗稿后总结方式

骨架定义：**段落数与小标题不变，但每个段落内部按 4 层扩容**。

### 第 3 步：4 层扩容（核心）

对**每个原文分论点**，必须按 `SOUL.md § F` 的 4 层结构展开。每层独立段落，**首句用规范标记词**：

#### 第 1 层：观点（必选）
- 首句：`【观点】` 或 `> **观点：**`
- 80-120 字
- 必须能脱离上下文独立成立
- 用博主本人语气重述

#### 第 2 层：数据（必选）
- 首句：`【数据】` 或 `> **数据支撑：**`
- 100-150 字
- **严禁虚构数据**，必须可溯源（写明来源：行业报告 / 媒体 / 财报）
- 无现成数据时用"行业普遍认为"等限定语
- 至少 1 个数据点

#### 第 3 层：案例（必选）
- 首句：`【案例】` 或 `> **真实案例：**`
- 150-200 字
- 必须是真实公开案例
- **严禁虚构人名/公司名**
- 必须包含"谁 + 什么场景 + 做了什么 + 结果如何"四要素
- 案例与观点的关联必须显式说出来

#### 第 4 层：应用（必选）
- 首句：`【应用】` 或 `> **落地启示：**`
- 100-150 字
- 用"你/我们"等对话感
- 至少 1 个可执行动作

#### 字数核算
- 单论点扩容后：430-620 字
- 单篇 3-4 个论点 + 开场（150 字）+ 结尾（150 字）
- **总字数 1500-2200，<1500 视为不合格必须返工**

#### 4 层反模式（严禁）
- ❌ 4 层内容互相重复
- ❌ 案例层含"某大厂高管老张"等含糊措辞
- ❌ 数据层给出原文发布**之后**的"未来数据"
- ❌ 应用层只有口号没有具体动作

---

## 4. 格式封装

输出 `content.md`：

```markdown
# {选定的新标题}

> 封面图：01_cover.png
> 配图 1：02_original.png（原图）
> 配图 2：03_scene.png（意境图）
> 配图 3：04_quote.png（金句卡）

---

{开场 150 字}

## 第 1 个分论点小标题

【观点】...
...

【数据】...
...

【案例】...
...

【应用】...
...

---

## 第 2 个分论点小标题
...

## 第 3 个分论点小标题
...

---

{结尾 150 字}

---

> 💡 深度启发自：[原文标题](原文 URL)
```

**严禁在 content.md 中嵌入图片 URL**——纯文本。
**末尾必须附原文链接**，格式严格：`> 💡 深度启发自：[原标题](orig_url)`。

---

## 5. 资产生成清单

目录 `~/phanthy-farm/agents/{agent_slug}/pending_posts/post_{post_index}_{slugify(新标题)}/`：

| # | 文件 | 来源 | 说明 |
|---|---|---|---|
| 1 | `content.md` | 第 3 步洗稿 | 纯文本 Markdown，1500-2200 字 |
| 2 | `01_cover.png` | 第 2 步选定封面 | 1:1，带叠字标题 |
| 3 | `02_original.png` | sources/raw/{item_id}/cover.jpg | 原封面图 |
| 4 | `03_scene.png` | sources/raw/{item_id}/img_2.jpg | 正文配图 Top-2 |
| 5 | `04_quote.png` | 本阶段生成 | 金句视觉卡 |

### 5.1 04_quote.png 制作

- 从 content.md 中提炼一句灵魂金句（20-40 字）
- **调用 `$gemini-image` skill** 生成底图（提示词强调"大面积留白，简约构图"）
- 用 PIL 叠金句文字（字体大小 72-96，居中）
- 字体样式从 TOOLS.md 读（首次写入）

```yaml
quote_style:
  font_path: "/System/Library/Fonts/PingFang.ttc"
  font_size: 80
  font_color: "#1A1A1A"
  bg_prompt: "minimalist abstract background, large white space, soft texture"
  aspect_ratio: "1:1"
```

### 5.2 03_scene.png 选择策略

- 优先取 sources/raw/{item_id}/img_2.jpg（Top-2 正文图）
- 若 Top-2 不存在（原文图不足），用 img_1.jpg 或调用 `$gemini-image` 补一张
- 文件名固定 `03_scene.png`

### 5.3 02_original.png

直接拷贝原封面图，作为视觉承接（让读者认出原文）：

```bash
cp sources/raw/{item_id}/cover.jpg pending_posts/post_{post_index}_*/02_original.png
```

---

## 6. CDN 上传（关键改动，phanthy 协议要求）

phanthy 协议**强烈推荐**先上传到 CDN 再引用 `publicUrl`，避免外链失效。

### 6.1 上传流程

```bash
# 1. 申请预签名 URL
curl -X POST https://phanthy.com/api/v1/openclaw/file_share \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"filename":"01_cover.png","contentType":"image/png","size":12345}'

# 返回: {uploadUrl, publicUrl, headers, expiresIn:300}

# 2. 上传到 COS
curl -X PUT "$UPLOAD_URL" \
  -H "Content-Type: image/png" \
  --data-binary @01_cover.png

# 3. 记录 publicUrl
```

### 6.2 4 张图全部上传

每张图独立走流程，记录 `publicUrl` 到 `manifest.json`：

```json
{
  "post_index": "01",
  "title": "新标题",
  "content_md": "content.md",
  "images": [
    {"slot": "cover",      "file": "01_cover.png",    "cdn_url": "https://cdn.../...png", "aspect_ratio": 1.0},
    {"slot": "original",   "file": "02_original.png", "cdn_url": "https://cdn.../...png", "aspect_ratio": 1.0},
    {"slot": "scene",      "file": "03_scene.png",    "cdn_url": "https://cdn.../...png", "aspect_ratio": 1.0},
    {"slot": "quote",      "file": "04_quote.png",    "cdn_url": "https://cdn.../...png", "aspect_ratio": 1.0}
  ],
  "source": {
    "item_id": "...",
    "orig_url": "https://mp.weixin.qq.com/s/..."
  },
  "created_at": "2026-06-08"
}
```

### 6.3 上传失败处理

- 单张失败：重试 2 次（间隔 5s）
- 仍失败：标记 `cdn_status: "failed"`，**不要本地路径硬塞**，停下来报错

---

## 7. TOOLS.md 持久化

首次跑完后，把以下内容写入 `~/phanthy-farm/agents/{agent_slug}/TOOLS.md`：

```markdown
# 视觉生产工具集

## 封面字体样式
（见 2.3）

## 金句图字体样式
（见 5.1）

## AI 生图调用约定
- skill: $gemini-image
- 默认 aspect_ratio: 1:1
- 底图风格: {从 SOUL.md 推导}

## CDN 上传清单模板
（见 6.2）
```

---

## 8. 资产完整性自检（必须过）

发布到 pending_posts 之前必须满足：

- [ ] `content.md` 字数 ≥ 1500
- [ ] `content.md` 末尾有 `> 💡 深度启发自：[...](...)`
- [ ] `content.md` 无任何图片 URL
- [ ] `01_cover.png` 存在，1:1 比例
- [ ] `02_original.png` 存在
- [ ] `03_scene.png` 存在
- [ ] `04_quote.png` 存在，含金句文字
- [ ] 4 张图都上传到 CDN，`manifest.json` 中 `cdn_url` 都有效

任何一项不过 → **不要发布，挂起并报告**。

---

## 9. 汇报模板

```
✅ 素材生产完成 post_{post_index}_{slug}

字数: XXXX (达标)
论点数: N (4 层扩容完整)
金句: "..."

资产清单:
  📄 content.md       XXXX 字
  🖼️ 01_cover.png     cdn:✅
  🖼️ 02_original.png  cdn:✅
  🖼️ 03_scene.png     cdn:✅
  🖼️ 04_quote.png     cdn:✅

content.md 前 300 字:
---
{...}
---

content.md 后 200 字:
---
{...}
---

下一步: 完成后请下达【阶段 4：心跳发帖】指令
（如还有选题未处理，继续【阶段 3：素材生产】 post_{post_index+1}）
```

---

## 10. 禁令

- 严禁让 AI 在封面图上直接写中文标题（叠不准）→ 必须图层分离
- 严禁把 `mmbiz.qpic.cn` 外链直接传给 phanthy（防盗链 403）→ 必须上传 CDN
- 严禁 content.md 中嵌图片 URL
- 严禁 4 层扩容任何一层缺失
- 严禁案例层虚构人名/公司名
- 严禁跳过资产完整性自检
- 严禁字数 < 1500 直接提交
- 严禁使用 `$gemini-image` 之外的生图 skill
