# 📦 一壶盐选（onehu-zhihu）· 素材补充提示词

> **本文件适用于已注册的 agent，仅做素材补充，不涉及注册/认领/心跳。**
> 把本文件完整复制粘贴给 Claude Code / Codex / Hermes，它会按流程加工素材并推送到 post/。

---

## 0. 你是谁

你在帮 **"一壶盐选"**（onehu-zhihu）这个 phanthy agent 补充素材库。

这个 agent **已经在 phanthy 注册过了**，线上正在运行。你的工作只是：
1. 从 `draft/` 里挑素材
2. 加工成可发布的成品
3. 放入 `post/`
4. git push

**你不做注册、不调 phanthy API、不碰心跳。**

---

## 1. 工作目录

```
AGENT_ROOT=~/phanthy-farm/agents/onehu-zhihu
```

**目录结构**：

```
agents/onehu-zhihu/
├── SOUL.md           ← 人设DNA（必读，理解角色）
├── TUNING.md         ← 加工参数（仿写策略、封面、正文图规范）
├── AGENT_RULES.md    ← 目录规则
├── PROFILE.md        ← 角色信息（了解即可）
├── 款式3_3x4.png     ← 封面/正文图共用背景
│
├── draft/            ← 原料仓（2945篇）
│   └── post_XXX_标题/
│       └── source.md
│
├── post/             ← 成品仓（你加工完放这里）
│   └── post_XXX_标题/
│       ├── content.md
│       ├── cover.png
│       └── body_pages/
│           ├── page_001.png
│           └── ...
│
└── archive_posts/    ← 已发布归档（不要动）
```

---

## 2. 加工流水线

**完整阅读 `TUNING.md`**，然后按以下步骤执行：

### Step 1：选题

从 `draft/` 中选取 N 篇（默认按编号从小到大，除非 owner 另外指定）。

```bash
ls $AGENT_ROOT/draft/ | sort | head -N
```

### Step 2：仿写

```bash
cd ~/phanthy-farm
python3 scripts/salt_rewrite.py --agent onehu-zhihu --count N
```

- 模型：glm-4.7（主力）
- 字数基准：12000 字（短文扩到 12000，长文 ±10%）
- 仿写完成后自动在 `post/` 生成对应目录和 content.md

### Step 3：AI 起标题

仿写完成后，用 AI 为每篇起新标题（≤15 字，书名式）。

**标题规则**（详见 SOUL.md §5）：
- 书名式，不要问句
- 不要带"知乎""盐选"等平台标识
- ≤15 个汉字
- 有悬念感

将新标题写入 content.md 第一行（替换原来的 `# 旧标题`）。

### Step 4：生成封面

```bash
python3 scripts/cover_generator.py --agent onehu-zhihu --count N
```

- 封面规范见 TUNING.md「封面设计 v9」
- 输出：`post/.../cover.png`（896×1200px）

### Step 5：生成正文图

```bash
python3 scripts/body_image_generator.py --agent onehu-zhihu --count N
```

- 正文图规范见 TUNING.md「正文配图 v1」
- 输出：`post/.../body_pages/page_001.png ~ page_NNN.png`（最多 20 张）

### Step 6：审计

每篇成品必须包含三件套：

```bash
for POST_DIR in $(ls -d $AGENT_ROOT/post/post_* | sort); do
  echo "审计: $(basename $POST_DIR)"
  [ -f "$POST_DIR/content.md" ] && echo "  ✅ content.md" || echo "  ❌ 缺 content.md"
  [ -f "$POST_DIR/cover.png" ] && echo "  ✅ cover.png" || echo "  ❌ 缺 cover.png"
  BODY=$(ls $POST_DIR/body_pages/*.png 2>/dev/null | wc -l)
  [ "$BODY" -gt 0 ] && echo "  ✅ body_pages ($BODY 张)" || echo "  ❌ 缺 body_pages"
done
```

**缺任何一项 = 不完整，不能推送。**

### Step 7：Git 推送

```bash
cd ~/phanthy-farm
git add agents/onehu-zhihu/post/
git commit -m "feat(onehu-zhihu): add N posts"
git push
```

线上 agent 会自动 git pull 拿到新素材。

---

## 3. 质量检查（可选）

如果 owner 要求检查质量，按 SOUL.md §6 风格自检清单：

- [ ] 标题 ≤15 字，书名式，无平台标识
- [ ] 摘要不剧透核心反转
- [ ] 正文无自己加的评论/观后感
- [ ] 字数达标（<12K 扩到 12K，≥12K 在 ±10% 内）
- [ ] 末尾有溯源链接
- [ ] 0 emoji、0 感叹号轰炸、0 夸张赞美

---

## 4. 关键纪律

- **不要动 `archive_posts/`**（那是已发布的内容）
- **不要修改已存在的 post/ 内容**（除非 owner 明确要求）
- **不要删 draft/ 里的原料**（用不完的留着）
- **不要注册、不要调 phanthy API、不要碰 CREDENTIALS.md**
- **不要批量跑超过 5 篇**（glm-4.7 限流风险）

---

**最后一句话**：你的工作就是"选料→加工→上菜→推送到仓库"。线上 agent 自己会拉素材发帖，你不用管。
