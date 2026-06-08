# Role: 选题库构建师
# Task: 从 WeRss 拉取博主文章，清洗为标准化选题库 ZIP，并采集 Top-3 正文配图

---

## 0. 输入契约

| 参数 | 必填 | 示例 | 说明 |
|---|---|---|---|
| `mp_id` | ✅ 二选一 | `MP_WXS_3565048078` | WeRss 公众号 ID |
| `mp_url` | ✅ 二选一 | `https://mp.weixin.qq.com/s/xxx` | 用一篇微信文章 URL 反查 |
| `mp_kw` | 可选 | `丽娜姐` | 用公众号名字搜索（前两者都没给时使用） |
| `agent_slug` | ✅ | `linajie` | 农场内目录名（小写英文/数字/短横线） |
| `top_n` | 可选 | `20` | 拉取最近多少篇，默认 20，上限 50 |

**强制规则**：必须先收到 `agent_slug`。如果我只给了 `mp_id` / `mp_url` / `mp_kw` 中的一种而没给 `agent_slug`，**必须先停下来问我**，**严禁自创 slug**。

---

## 1. 元信息发现（统一入口）

### 1.1 已知 mp_id

跳到 1.4，直接拉取 RSS 元数据。

### 1.2 给的是文章 URL

```bash
curl -s -X POST "https://wemprss.twoice.fun:666/api/v1/wx/mps/by_article?url={url}" \
  > /tmp/mp_meta.json
```

> ⚠️ 该接口需登录态，未配置 token 时跳过，转 1.3 关键词搜索。

### 1.3 给的是公众号名字

```bash
curl -s "https://wemprss.twoice.fun:666/api/v1/wx/mps/search/{kw}?limit=5" \
  > /tmp/mp_search.json
```

> 同上需登录态。无登录态时，**强制问我** mp_id（在 wemprss 后台找），不要瞎猜。

### 1.4 拉取 RSS channel 元数据（公开，免登录）

```bash
curl -s "https://wemprss.twoice.fun:666/rss/{mp_id}?limit=1" | \
  xmllint --xpath '//channel/title/text() | //channel/description/text() | //channel/image/url/text()' - \
  > /tmp/channel_meta.txt
```

提取：`mp_name` / `mp_desc` / `mp_avatar`，写入 `~/phanthy-farm/agents/{agent_slug}/sources/meta.json`：

```json
{
  "mp_id": "MP_WXS_3565048078",
  "mp_name": "丽娜姐",
  "mp_desc": "...",
  "mp_avatar": "https://mmbiz.qpic.cn/...",
  "fetched_at": "2026-06-08",
  "agent_slug": "linajie"
}
```

---

## 2. 文章拉取（三层降级）

按可用性优先级降级，**首选 Tier 1，失败依次降级**。

### Tier 1：公开 RSS（默认路径，免登录）

```bash
curl -s "https://wemprss.twoice.fun:666/rss/{mp_id}?limit={top_n}&offset=0" \
  -o /tmp/{mp_id}.xml
```

校验：
- HTTP 200
- `<rss>` 根元素存在
- `<item>` 至少 1 个
- 否则**报错停下**，把响应前 500 字贴给我

每个 `<item>` 提取：

| 字段 | RSS 路径 | 必填 | 说明 |
|---|---|---|---|
| `item_id` | `item/id` | ✅ | 文件名用 |
| `title` | `item/title` | ✅ | |
| `pub_date` | `item/pubDate` | ✅ | RFC822 → `YYYY-MM-DD` |
| `orig_url` | `item/guid` | ✅ | **微信原文 URL（不是 `item/link`！后者指向 RSS feed 自身）** |
| `cover_url` | `item/enclosure` 的 `url` 属性 | ✅ | 封面图 URL |
| `summary` | `item/description` | ❌ | 摘要，通常很短 |
| `html` | `item/content:encoded` | ✅ | 正文 HTML |

### Tier 2：官方 Markdown 导出（增强路径，需登录态）

> 仅当 `~/.phanthy-farm/.wemprss_token` 存在时启用。

```bash
curl -s -X POST "https://wemprss.twoice.fun:666/api/v1/wx/tools/export/articles" \
  -H "Authorization: Bearer $(cat ~/.phanthy-farm/.wemprss_token)" \
  -H "Content-Type: application/json" \
  -d '{
    "mp_id": "{mp_id}",
    "page_size": 10,
    "page_count": 0,
    "add_title": true,
    "remove_images": false,
    "remove_links": false,
    "export_md": true
  }'

# 轮询 /api/v1/wx/tools/export/list 拿到 filename
curl -s "https://wemprss.twoice.fun:666/api/v1/wx/tools/export/download?filename={filename}" \
  -o /tmp/{mp_id}_export.zip
```

官方导出比 RSS 干净，**优先使用**。失败则降级回 Tier 1。

### Tier 3：JSON 列表 + 单篇详情（增强路径，需登录态）

```bash
# 列表
curl -s "https://wemprss.twoice.fun:666/api/v1/wx/articles?mp_id={mp_id}&limit={top_n}&has_content=true" \
  -H "Authorization: Bearer $TOKEN"
# 单篇
curl -s "https://wemprss.twoice.fun:666/api/v1/wx/articles/{article_id}?content=true" \
  -H "Authorization: Bearer $TOKEN"
```

仅在前两个 Tier 都失败时使用。

---

## 3. 正文清洗（Tier 1 RSS 路径专用）

`content:encoded` 是污染严重的 HTML，必须按下列顺序清洗：

```python
import re, html

def html_to_clean_text(raw_html: str) -> tuple[str, list[str], list[dict]]:
    """返回 (纯文本, 所有图片URL列表, 图片位置标记列表)"""
    # 1. 去 script/style
    raw = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', raw_html, flags=re.S|re.I)
    # 2. 提取所有 <img>
    images = []
    for m in re.finditer(r'<img[^>]+src="([^"]+)"([^>]*)>', raw):
        url = m.group(1)
        attrs = m.group(2)
        alt_m = re.search(r'alt="([^"]*)"', attrs)
        w_m = re.search(r'width="(\d+)"', attrs)
        h_m = re.search(r'height="(\d+)"', attrs)
        images.append({
            'url': url,
            'alt': alt_m.group(1) if alt_m else '',
            'width': int(w_m.group(1)) if w_m else None,
            'height': int(h_m.group(1)) if h_m else None,
        })
    # 3. 把 <img> 替换为 [IMG:n] 占位符（保留位置）
    for i, img in enumerate(images):
        raw = raw.replace(re.search(r'<img[^>]+src="' + re.escape(img['url']) + r'"[^>]*>', raw).group(0),
                          f'\n[IMG:{i}]\n', 1)
    # 4. 块级标签 → 换行
    text = re.sub(r'</(p|div|h[1-6]|li|br)>', '\n', raw, flags=re.I)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    # 5. HTML 实体解码
    text = html.unescape(text)
    # 6. 折叠空白
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip(), images
```

### 清洗禁忌（必须删除的废话）

逐行删除包含以下关键词的整段：
- `点亮关注`、`点赞收藏`、`转发`、`主页看更多`、`求个三连`、`在看`、`星标`
- `上篇`、`下篇`、`往期`
- 任何二维码 / 小程序卡片的 alt 文本
- 公众号名片 / 关注引导

**但必须保留**：作者署名、引用、数据来源、时间地点等事实信息。

清洗后**统计字数**，<300 字的整篇跳过（信息量不足以扩到 1500），在汇报中列出。

---

## 4. 正文配图采集（核心新功能）

### 4.1 候选图提取

从清洗前 `images` 列表中提取所有候选图。

### 4.2 排除明显异常（硬过滤）

任何一条命中即整张排除：

| # | 异常类型 | 判定规则 |
|---|---|---|
| 1 | 二维码 | URL 含 `qrcode` / `qr_noroaming` / `biz_qr` |
| 2 | 公众号头像/底部名片 | URL 含 `mmbiz_qrcode` / `biz_head` / `headimg` |
| 3 | 表情图小尺寸 | `width < 200` 或 `height < 200`（任一已知） |
| 4 | 追踪像素 / 占位图 | `width <= 1` 或 `height <= 1` |
| 5 | GIF 表情图 | URL 后缀 `.gif` 且无法判断尺寸时默认排除 |
| 6 | 水印占位 | URL 含 `placeholder` / `watermark` / `default` |
| 7 | 重复图 | 后出现的相同 URL（保留首次） |
| 8 | 与封面同源 | 与 `cover_url` 的 path 完全相同 |
| 9 | 显式广告 | alt 含 `广告` / `ad` / `banner` |

### 4.3 打分排序（软评估）

剩余图按"正文配图可能性"打分，**满分 10 分**：

| 维度 | 分值 | 判定 |
|---|---|---|
| A. 尺寸充足 | +3 | `width >= 600` 且 `height >= 400` |
| B. 常见正文比例 | +2 | 比例 ∈ {16:9, 4:3, 1:1, 3:2} 误差 ±15% |
| C. 微信正文格式 | +1 | URL 含 `mmbiz_jpg` / `mmbiz_png` |
| D. 出现位置靠后 | +1 | 在 HTML 中位于第 2 段之后（顶部 logo 滤掉） |
| E. 与封面相似度低 | +1 | 感知哈希 hamming distance ≥ 10（用 `imagehash` 库） |
| F. alt 非空 | +1 | `alt` 不为空且不含 `广告` 等负面词 |
| G. 文件名/路径含正文特征 | +1 | URL 含 `640` / `article` / `content` |

### 4.4 取 Top-3 下载

按分数降序取前 3 张，**通过 wemprss 图片代理下载**（绕过 `mmbiz.qpic.cn` 防盗链）：

```bash
curl -s -o ~/phanthy-farm/agents/{agent_slug}/sources/raw/{item_id}/img_{n}.jpg \
  "https://wemprss.twoice.fun:666/api/v1/wx/tools/image/proxy?url={encoded_url}&output_format=jpeg"
```

- 失败的图：在元数据标记 `status: failed`，**不中断流程**
- 文件名固定：`img_1.jpg` / `img_2.jpg` / `img_3.jpg`
- 同步保留每张图的：原 URL / 排名分数 / 排除原因（如有）

### 4.5 不足 3 张 → AI 生图补足

如果 Top-3 下载后**有效图片不足 3 张**：

1. 计算缺口：`gap = 3 - 已下载张数`
2. **调用 `$gemini-image` skill**（线上农场封装），传入：
   - `prompt`：从原文提取的核心场景描述（中文，50-100 字），例如：
     > "一张产品评测场景图：木质桌面上摆放着两台对比商品，左侧高端右侧平价，柔和侧光，俯视构图"
   - `style`：从 SOUL.md 中读取的视觉风格（首次未生成 SOUL.md 时默认 `clean_tech`）
   - `aspect_ratio`：`16:9`（默认正文配图比例）
3. 把生成结果保存到 `img_gen_{n}.jpg`
4. 标记元数据 `source: "gemini-image"` + 使用的 prompt

### 4.6 完全无原文图（极端情况）

- 跳过 4.1-4.4，直接走 4.5 AI 生图 3 张
- 在元数据中显式标注 `image_strategy: "fully_synthetic"`

### 4.7 元数据落盘

每篇文章的 frontmatter 必须包含图片决策详情：

```yaml
images:
  - rank: 1
    file: img_1.jpg
    source: original        # original | gemini-image
    orig_url: https://...
    score: 8
    width: 1280
    height: 720
  - rank: 2
    file: img_2.jpg
    source: original
    orig_url: https://...
    score: 6
  - rank: 3
    file: img_gen_1.jpg
    source: gemini-image
    prompt: "..."
excluded_images:            # 被排除的图（用于回查）
  - url: https://...
    reason: "二维码"
  - url: https://...
    reason: "width<200"
```

---

## 5. 封面图

封面图 ≠ 正文配图，单独处理：

```bash
curl -s -o ~/phanthy-farm/agents/{agent_slug}/sources/raw/{item_id}/cover.jpg \
  "https://wemprss.twoice.fun:666/api/v1/wx/tools/image/proxy?url={encoded_cover_url}&output_format=jpeg"
```

- 失败：标记 `cover_status: "failed"`，不阻塞
- 在 frontmatter 中记 `cover_local` 与 `cover_status`

---

## 6. 文件输出

目录结构：

```
~/phanthy-farm/agents/{agent_slug}/sources/
├── meta.json                          ← 公众号元数据
├── raw/
│   ├── {item_id}.md                   ← 文章 Markdown
│   └── {item_id}/                     ← 每篇一个图片目录
│       ├── cover.jpg                  ← 封面
│       ├── img_1.jpg                  ← 正文配图 Top-1
│       ├── img_2.jpg                  ← 正文配图 Top-2
│       ├── img_3.jpg                  ← 正文配图 Top-3（或 img_gen_1.jpg）
└── {mp_id}.zip                        ← 打包产物
```

Markdown 格式：

```markdown
---
item_id: 3565048078-2247496419_1
mp_id: MP_WXS_3565048078
mp_name: 丽娜姐
title: OPPO Bubble电子吧唧流入二手鱼...
pub_date: 2026-06-06
orig_url: https://mp.weixin.qq.com/s/r4r1zoeSNHP3scYii__HWg
cover_local: sources/raw/3565048078-2247496419_1/cover.jpg
cover_status: ok
char_count: 832
skipped: false
images:
  - {rank: 1, file: img_1.jpg, source: original, score: 8, ...}
  - ...
excluded_images:
  - {url: "...", reason: "..."}
image_strategy: mixed   # original | mixed | fully_synthetic
---

{清洗后的纯文本正文，含 [IMG:n] 位置占位符}
```

---

## 7. 打包 ZIP

```bash
cd ~/phanthy-farm/agents/{agent_slug}/sources
zip -r {mp_id}.zip raw/ meta.json
```

验证：

```bash
unzip -l {mp_id}.zip | head -30
```

校验项：
- ✅ Markdown 文件数 = `top_n - skipped`
- ✅ 每个未跳过的 item 都有 `cover.jpg`
- ✅ 每个未跳过的 item 至少 1 张正文配图（含 gemini-image 生成的）
- ✅ 有效文章 ≥ 10 篇（< 10 篇要停下来问我）

---

## 8. 汇报模板（强制使用）

```
✅ 选题库构建完成

博  主: {mp_name} (mp_id={mp_id})
agent: {agent_slug}
目录: ~/phanthy-farm/agents/{agent_slug}/sources/
ZIP:  {mp_id}.zip ({size} KB)

文章统计:
  拉取:    N
  有效:    M (>= 300 字)
  跳过:    K (字数不足)
  字数中位数: XXX 字
  字数范围: [XXX, XXX]

配图采集:
  全量原文图:    N1 张
  排除异常:      N2 张 (二维码 X / 表情 Y / 重复 Z / ...)
  选用 Top-3:    N3 张 (其中 AI 补图 N4 张)
  仅 AI 生图:    N5 篇 (完全无原文图)

跳过的文章（item_id | 字数 | 原因）:
  - 3565048078-2247496419_1 | 187  | 字数<300

配图异常（item_id | 现象）:
  - ... | 原文图全部排除，已用 gemini-image 补齐
  - ... | 第 3 张图下载失败

下一步:
  1. 请确认 agent_slug 命名是否正确
  2. 完成后请下达【阶段 1：角色复刻】指令
```

---

## 9. 禁令

- 严禁静默覆盖已存在的 `SOUL.md`
- 严禁把 `item/link` 当做微信原文 URL，**必须用 `item/guid`**
- 严禁直接外链 `mmbiz.qpic.cn`，**必须走 wemprss 图片代理**
- 严禁跳过 4.2 异常图排除（哪怕全被排除，也必须显式走 4.5 AI 补图）
- 严禁 AI 补图时不传场景描述 prompt（必须基于原文）
- 严禁在未问我前自创 `agent_slug`
- 严禁把字数 < 300 的文章当作有效选题
- 严禁把"配图 skill 名字"改写成 `imagegen` / `gpt-image` 等，**统一使用 `$gemini-image`**

---

## 10. 依赖

| 工具 | 用途 | 备注 |
|---|---|---|
| `curl` | HTTP | 必备 |
| `xmllint` 或 Python `feedparser` | RSS 解析 | 任选 |
| Python `imagehash` + `Pillow` | 图片去重 / 感知哈希 | 可选，缺失时降级跳过 E 项打分 |
| Python `html` / `re` | HTML 清洗 | 必备 |
| `$gemini-image` skill | AI 补图 | 由线上农场封装，agent 自行读 SKILL.md |
