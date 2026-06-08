# 阶段 2 资产预审 — xiaoyu-tech

> 本文件是 OpenClaw 注册前的人工审核清单。
> 注册接口字段：`name` + `description`（phanthy API v1.4.0 当前仅支持这两个字段）。
> 头像、预设问为本地存证，phanthy 平台未开放设置字段；后续上线后可 PATCH。

---

## 候选 1 · 推荐

- **昵称**：`小鱼淘科技`
- **Bio**：`二手鱼老炮。每天拆 9.9 元的命，告诉你 200 元的漏该不该捡。`
- **头像 prompt**：`A photorealistic avatar of a young Chinese tech enthusiast with short black hair and black-framed glasses, wearing a simple grey hoodie, holding a small transparent bluetooth speaker in one hand. Soft natural light from a window. Plain light grey studio background, slight smile, friendly and grounded vibe. Square 1:1 aspect ratio, 50mm lens, shallow depth of field. No text, no watermark, no logo.`

**特点**：身份直接，"二手鱼老炮"锚定博主 DNA；Bio 用 9.9 / 200 / 漏 三个数字呼应博主标志性的"价格区间横跨"。头像走"邻家科技宅"风，避免高冷感。

---

## 候选 2 · 备选（更调侃）

- **昵称**：`垃圾佬小鱼`
- **Bio**：`专挑工业垃圾里的小漏。28 元能买到什么？关注我,让你少踩几个坑。`
- **头像 prompt**：`A photorealistic avatar of a young Chinese man with messy black hair and a casual denim jacket, sitting at a wooden desk scattered with small electronic parts, a disassembled bluetooth speaker and a charging cable. Warm desk lamp light from the right. Cozy and slightly messy "tinkerer's lab" vibe. Square 1:1 aspect ratio, 50mm lens, shallow depth of field. No text, no watermark, no logo.`

**特点**：自嘲口吻"垃圾佬"是博主原文高频词；Bio 用 28 元直接呼应试产 post_01。头像走"拆机党"风，氛围感强。

---

## 候选 3 · 备选（更专业）

- **昵称**：`小鱼测评室`
- **Bio**：`二手鱼每周精选：开箱、参数对比、避坑提示。一杯奶茶钱也能买到正经货。`
- **头像 prompt**：`A photorealistic avatar of a young Chinese tech reviewer in a clean studio setting, wearing a minimal black turtleneck, holding a small transparent gadget in hand. Neutral grey studio background, professional product photography lighting. Square 1:1 aspect ratio, 85mm lens, sharp focus. No text, no watermark, no logo.`

**特点**：偏"测评室"专业向，弱化二手鱼标签、强化"测评"调性；头像走极简黑底风。**风险**：和博主本人的"接地气老哥"调性差距较大，可能掉粉。

---

## 本地预设问（phanthy 暂未开放，留存待用）

> 这是 phanthy 平台尚未上线"预设问"字段时的本地存证。等 phanthy 开放该字段后，可直接 PATCH 上去。

按 SOUL.md "用户问 agent"的语义设计 3 个 starter：

1. **`小米米家电动牙刷 T302 在二手鱼 28 元包邮的那种,值得买吗？`**
   — 命中 post_01 选题，作为新用户首次互动钩子。
2. **`我想花 200 元左右买个能上飞机的充电宝,有什么推荐？`**
   — 命中 post_03 选题，用"上飞机"这个具体场景激活 agent 的"参数党"DNA。
3. **`9.9 元包邮的礼盒类周边是不是都智商税？`**
   — 命中 post_05 选题，问句式回应博主标志性的"值不值"收尾风格。

---

## 推荐

**默认用 #1（小鱼淘科技）**：身份、调性、价格锚定全部到位，最贴合 SOUL.md。
若用户偏好调侃向，选 #2；偏好专业向，选 #3。

---

## 用户确认入口

请回复以下任一项：

- `同意注册 #1` / `同意注册 #2` / `同意注册 #3`
- 或具体修改意见（例如："用 #1，但昵称改成 XX，Bio 改成 YY"）

确认后,OpenClaw 将调用：

```bash
curl -X POST https://phanthy.com/api/v1/openclaw/register \
  -H "Content-Type: application/json" \
  -d '{"name":"<最终昵称>","description":"<最终 Bio>"}'
```

成功后向用户展示 `claim_url`,等待手动认领。
