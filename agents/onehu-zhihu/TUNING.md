# 精调文档：onehu-zhihu

> 本文档记录针对此 agent 的所有个性化配置，在对话中持续迭代。

## 仿写策略

- 字数基准线：**12000 字**（2026-06-10 定）
  - 原文 < 12000 字 → **扩写到 12000 字**
  - 原文 ≥ 12000 字 → 仿写后字数与原文相差不超过 ±10%
  - 质量判定（用户 2026-06-10 明确）：**只看下限（不低）**——超过目标上限不警告、不重试、不截断
- 主力模型：**glm-4.7**（需 thinking:disabled，max_tokens=65536）
  - 备选：MiniMax-M2.7（仅当用户明确要求或 4.7 限流时使用）
- 脚本：`scripts/salt_rewrite.py --agent onehu-zhihu --count N`
- 标题：仿写完成后用 glm-4-flash 起新标题（≤15字书名式），写入 content.md 第一行，再生成封面+正文图
- 仿写 prompt v2 要点：扩写方向按优先级（转折铺垫>心理/潜台词>环境描写），加禁止注水条款

## 封面设计（v9 规范，2026-06-10 定稿）

### 基本信息
- 尺寸：896×1200px（3:4 比例）
- 背景：`agents/onehu-zhihu/款式3_3x4.png`（浅灰水墨风格）
- 字体：Pillow fallback 链（wqy-zenhei → PingFang → STHeiti → Hiragino → Songti → 微软雅黑）

### 布局结构

| 元素 | 位置/属性 | 备注 |
|------|-----------|------|
| 顶部字数 | Y=130，32号字，#999999 浅灰 | `全文{N}字 · 阅读需{M}分钟`（M=max(1, N//400)）|
| 标题 | Y=340 起，自适应字号（100→80→72→64→56→50→44 循环），#2d2d2d，8 方向描边 #8b7355 3px | **最多 2 行**，左右各 80px 边距硬性保证 |
| 摘要 | 起始 Y=460（动态 max(460, 标题末行 Y+100)）| 26号字 #555555，行高 36px，段间空行 24px（≈0.7 倍行高）|
| 装饰线 | 摘要结束 + 30px | 双短横线 + 菱形 #8b7355 |
| CTA 按钮 | H-50 居中 | 圆角矩形 #8b7355 + 白字"点击阅读全文" 36号（h=68, 宽 +80）|

### 间距比例（v8 用户定稿）
- 顶部 ↔ 标题：**210px**（最大间距，让标题"飘"起来）
- 标题 ↔ 摘要：**100px**（保证呼吸感，不让标题和摘要粘连）
- 摘要段间：**24px**（小到能看出分段但不喧宾夺主）

### 标题换行算法 v3
- 虚词绑定：`之的了和与或但而却也还都已着过及其`（行末虚词+下一字绑定，解决"之谜"被拆）
- 介词绑定：`上中下里外内前后左右`（前接实词绑定，解决"地球上"被拆）
- 标点不参与绑定（避免"之？"怪组合）
- 不加"地""得"（既是虚词又是实词，会误伤）
- 短标点附加到上一行

### 标题自适应字号（v9 核心）
```python
SIDE_MARGIN = 80
target_width = W - 2 * SIDE_MARGIN  # 736
for size in [100, 80, 72, 64, 56, 50, 44]:
    font_test = ImageFont.truetype(font_path, size)
    char_w = font_test.getbbox("中")[2]
    mc = max(1, int(target_width / char_w))
    lines = wrap_title(title, max_chars=mc)
    if len(lines) <= 2:
        title_font_size = size
        max_chars = mc
        title_lines = lines
        break
```

### 摘要提取规则
- 跳过：`# ` 标题 / `> ` 引用 / `（N）` 章节 / 空行 / `💡` 溯源
- 合并所有清洗行 → 用**保留标点的正则**取前 200 字符
- 超过 200 字则末尾加 `…`
- 段切：按 `。！？\n` 切分；每 2 句合并为一段
- 段内按 ≤25 字**软切**（优先在标点处切）
- 段间加空行标记

### 用户决策记忆
- 不要作者署名（删了 "by onehu · 盐选小说精选"）
- 标题最多 2 行（超过自动降字号）
- 标题左右各 80px 固定边距
- 顶部-标题间距要大（210px）
- 标题-摘要间距要大（100px）
- 摘要段间距要小（24px）

### 脚本
- `scripts/cover_generator.py --agent onehu-zhihu --count N`

## 正文配图（v1 规范，2026-06-10 定稿）

### 基本信息
- 尺寸：896×1200px（3:4 比例）
- 背景：`agents/onehu-zhihu/款式3_3x4.png`（与封面共用）
- 字体：Pillow fallback 链（同上）

### 布局结构

| 元素 | 位置/属性 | 备注 |
|------|-----------|------|
| 标题 | Y=50，40号字，居中，#8b4513（saddle brown）| 自动换行最多 2 行（14 字/行）|
| 分隔线 | Y=75（标题下 25px），#cccccc 1px | 横贯 |
| 正文 | Y=120 起，**24号字，行高 59px，每行 33 字** | 17 行/页 |
| 左边距 | 60px | |
| 右边距 | 40px | |
| 页码 | Y=1180，18号，#888888，居中 | "第 N/M 页" |
| 文字颜色 | #2d2d2d（深灰） | |

### 关键修复：按段落切分
```python
# ❌ 错误：按整字符流硬切（会跨段落拼接）
page_content = content[start:end]
lines = [page_content[i:i+33] for i in range(0, len(page_content), 33)]

# ✅ 正确：按段落分别切分（保留段落结构）
paragraphs = content.split('\n')
all_lines = []
for para in paragraphs:
    if not para.strip():
        continue
    for i in range(0, len(para), 33):
        all_lines.append(para[i:i+33])
```

### 重要细节
- 标题 2 行时**分隔线/正文 Y 必须动态下移**（不能硬编码 Y=75 和 Y=120）
- 40 号字真实高度 38px，line_height ≥ 48（1.2× 字号）
- 1 行标题：divider_y ≈ 90，text_y ≈ 115
- 2 行标题：divider_y ≈ 138，text_y ≈ 163

### 用户决策记忆
- **段间不加空行**（2026-06-10 用户原话："段间空行不需要，新再这样就很好了，看着也不累"）
- 段间视觉分隔靠 24 号字行间 35px 行距自然形成
- 标题最多 2 行 OK，超过则用完整原标题

### 实际效果（post_1498 测试）
- 标题："战争胜利后，潜伏在敌后的谍报人员结局怎样？"（22 字 → 2 行 14+8）
- 12.7K 字 → 468 行 → 28 页

### 脚本
- `scripts/body_image_generator.py --agent onehu-zhihu --folder "post_XXX_..."`
- 输出：`post/.../body_pages/page_001.png` ~ `page_NNN.png`

## 发帖规范

（待精调）

## 调性/语气

（待精调）
