# 02_cover · 封面 Prompt（策略 C：1 推荐 + 2 备选）

> 龙虾农场 OpenClaw 调 `gemini-image` 默认用 **#1**。
> **严禁**叠加中文文字（标题由 phanthy 平台卡片单独渲染）。

---

## #1 · 推荐（默认）

**用途**：突出礼盒整体感 + 价格冲击力，符合"品牌礼盒捡漏"DNA。

```
A product hero shot of a clean white gift box lying diagonally on a textured concrete-grey surface, slightly opened to reveal a small white camera bag and a folded selfie stick peeking out. Beside the box: three small kraft paper tags with the number "50" printed in bold black marker. Soft directional light from top-left casting subtle shadow. Color grading: warm beige and cool steel grey, slightly desaturated secondhand-market vibe. Clean minimal composition, 1:1 square aspect ratio, photorealistic, 50mm lens, shallow depth of field. No text, no watermark, no readable brand logo on the box.
```

**关键控制点**：1:1 正方形 / 物品斜放 = 随手摆拍感 / "50" 写在小纸片上 = AI 写阿拉伯数字稳 / 不要可识别的 OPPO logo。

---

## #2 · 备选（场景向）

**用途**：放入使用场景，强调"通勤副包"实用性。

```
A flat-lay still life photograph, top-down view, on a warm wooden desk. A small white canvas camera bag (about the size of a thick paperback book) with a folded selfie stick placed beside it. A smartphone in the upper-right corner showing a secondhand marketplace app (blurred generic interface). Warm natural window light from the right, soft shadow. Color palette: cream, light wood, soft white. Square 1:1 aspect ratio, lifestyle photography aesthetic, shallow depth of field. No text overlay, no watermark, no readable brand logo.
```

---

## #3 · 备选（极简向）

**用途**：突出"全新未拆封"的精致感，适合追求极简的用户。

```
A single sealed white gift box, centered, on a pure light grey seamless background. The box is photographed from a 45-degree front angle, soft shadow beneath. Minimalist composition, premium product photography aesthetic. Soft directional studio light. Square 1:1 aspect ratio, 85mm lens, photorealistic, sharp focus. No overlay text, no watermark, no readable brand markings.
```

---

## 调度建议

- 默认用 **#1**。失败 3 次回退 #2，再失败 #3，再失败 → 跳过本篇。
- 输出 1:1 PNG/JPG，分辨率 ≥ 1024×1024。
