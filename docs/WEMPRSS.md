# WeRss 接口契约（v2）

> 用于把微信公众号博主文章拉成结构化选题库。
> 服务地址：`https://wemprss.twoice.fun:666`
> Swagger UI：`/api/docs`
> OpenAPI Spec：`/api/openapi.json`

## 1. 认证体系

| 类型 | 用途 | 适用范围 |
|---|---|---|
| OAuth2 Password Flow | 用户登录 | `/api/v1/wx/*` 几乎全部接口 |
| Access Key + Secret Key | 级联子节点身份 | 仅 `/api/v1/wx/cascade/*` |
| 无认证 | 公开访问 | `/rss/*` / `/feed/*` / `/views/*` |

### 1.1 OAuth2 用户登录

```bash
curl -X POST https://wemprss.twoice.fun:666/api/v1/wx/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=USER&password=PASS&grant_type=password"
```

返回 JWT token，写入 `~/.phanthy-farm/.wemprss_token`，所有受保护接口用：
```
Authorization: Bearer {token}
```

### 1.2 Access Key / Secret Key

**重要**：AK/SK **不是给 REST API 当 bearer 用的**，是给 wemprss 级联子节点用的（`/cascade/*` 接口）。

如果给我的 AK/SK：`WKWztGp8WvvrO4eMr9FDN-JvnSlrV8k6xN` / `SKBhHGBuzzHGs7U7JFwCNk2dDvnBeaCN7Y`，预期用途：
- 给一个独立的 wemprss 子节点部署做心跳/抓取上报
- 8 种常见传递方式（X-Access-Key/X-API-Key/Bearer/query...）均返回 401
- 真实签名方案 OpenAPI 没暴露，按"不可用于 REST"对待

**对选题库构建场景，无需 AK/SK 也无需登录态**——公开 RSS 足够。

---

## 2. 三层拉取路径

### Tier 1：公开 RSS（默认）

```
GET /rss/{mp_id}?limit=N&offset=M&kw=K
```

- 无需认证
- 返回 `application/rss+xml`
- 支持 `limit` / `offset` / `kw` 分页检索
- 每条 `<item>` 含 `content:encoded` 完整正文 HTML

字段映射：

| RSS 字段 | 说明 |
|---|---|
| `item/id` | 文章 ID，如 `3565048078-2247496419_1` |
| `item/title` | 标题 |
| `item/pubDate` | 发布时间（RFC822） |
| `item/guid` | **微信原文 URL（不是 link！）** |
| `item/enclosure@url` | 封面图 URL |
| `item/content:encoded` | 正文 HTML |

### Tier 2：官方 Markdown 导出（增强）

```
POST /api/v1/wx/tools/export/articles
GET  /api/v1/wx/tools/export/list
GET  /api/v1/wx/tools/export/download?filename=...
```

- 需 OAuth2 登录态
- 可一键导出 Markdown / DOCX / JSON / CSV / PDF
- 输出比 RSS 干净，避免 HTML 清洗

`ExportArticlesRequest` 字段：

```json
{
  "mp_id": "MP_WXS_xxx",
  "doc_id": [],                  // 文章 ID 列表，空则全部
  "page_size": 10,               // 1-10
  "page_count": 0,               // 0=全部
  "add_title": true,
  "remove_images": false,        // 保留图片
  "remove_links": false,
  "export_md": true
}
```

### Tier 3：JSON 列表 + 单篇详情

```
GET  /api/v1/wx/articles?mp_id=&limit=&has_content=true
GET  /api/v1/wx/articles/{article_id}?content=true
```

- 需 OAuth2 登录态
- 用于精细控制（如单篇刷新 `POST /articles/{id}/refresh`）

---

## 3. 图片处理

### 3.1 图片代理（关键能力）

```
GET /api/v1/wx/tools/image/proxy?url={encoded}&output_format=jpeg&width=&height=&aspect_ratio=&mode=
```

- **解决 `mmbiz.qpic.cn` 防盗链**
- 实测公开访问可用（不需要登录态）
- 支持参数：`aspect_ratio`（如 `16:9`）、`width`、`height`、`mode`（裁剪方式）、`output_format`（png/jpeg/webp）

### 3.2 图片裁剪

```
POST /api/v1/wx/tools/image/crop
```

需要登录态，主要用于二次裁剪。

---

## 4. 公众号发现

| 场景 | 接口 | 认证 |
|---|---|---|
| 已知 mp_id | 直接用 | 无 |
| 用文章 URL 反查 mp | `POST /api/v1/wx/mps/by_article?url=` | OAuth2 |
| 用名字搜索 | `GET /api/v1/wx/mps/search/{kw}` | OAuth2 |
| 查公众号详情 | `GET /api/v1/wx/mps/{mp_id}` | OAuth2 |

---

## 5. 关键陷阱

1. `item/link` 指向 RSS feed 自身，**原文链接用 `item/guid`**
2. `content:encoded` 含大量 `<span style="visibility: visible;">` 包裹，需要清洗
3. `mmbiz.qpic.cn` 带防盗链，**直接外链 403**，必须走图片代理
4. RSS 无"标记已用"机制，需自己在 `progress.json` 维护已抓取文章 ID 集合
5. **AK/SK 不可用于 REST API 认证**——如果给了 AK/SK 别拿它当 Bearer 用
6. 公众号搜索/反查接口都需要登录态，无登录态时**强制人工提供 mp_id**

---

## 6. 推荐拉取流程

```
1. 元信息: GET /rss/{mp_id}?limit=1  → meta.json
2. 文章列表: GET /rss/{mp_id}?limit=N&offset=0  → XML
3. 解析: feedparser / xmllint
4. 正文清洗: 去 script/style/嵌套 span, 提图片占位符
5. 配图采集:
   - 候选图 → 异常排除 → 打分 → Top-3
   - 通过 /tools/image/proxy 下载（解决防盗链）
   - 不足 3 张 → $gemini-image skill 补足
6. 封面图: 走 /tools/image/proxy 单独下载
7. 落盘: sources/raw/{item_id}.md + sources/raw/{item_id}/*.jpg
8. 打包: sources/{mp_id}.zip
```
