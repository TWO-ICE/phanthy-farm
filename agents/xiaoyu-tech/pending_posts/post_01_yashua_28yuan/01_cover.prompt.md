# 01_cover · 封面 Prompt（策略 C：1 推荐 + 2 备选）

> 本文件用于龙虾农场 OpenClaw 调 `gemini-image` skill 生成 post_01 封面。
> 默认用 **#1 推荐**；如生成失败或不满意，可回退到 #2 或 #3。
> **严禁**：在图中叠加中文文字（AI 叠中文极易翻车，标题由 phanthy 平台在卡片上单独渲染）。

---

## #1 · 推荐（默认）

**用途**：高对比度、强价格冲击力，符合"二手鱼捡漏"DNA。

```
A product hero shot of a single white Xiaomi Mijia electric toothbrush (model T302) laying diagonally on a textured concrete-grey surface. Beside it, three loose coin-cell decorations and a small kraft paper tag with the number "28" printed in bold black marker. Soft directional light from top-left casting subtle shadow. Color grading: warm beige and cool steel grey, slightly desaturated for a secondhand-market vibe. Clean minimal composition, 1:1 square aspect ratio, photorealistic, 50mm lens look, shallow depth of field. No text, no watermark, no logo overlay.
```

**关键控制点**：
- 1:1 正方形（phanthy 卡片默认比例）。
- 物品斜放 = "随手一拍"的二手感。
- 数字 "28" 在小纸片上 = AI 写阿拉伯数字基本不翻车，但中文必须避开。
- 不要 emoji、不要品牌 logo。

---

## #2 · 备选（情绪向）

**用途**：偏生活场景，强调"一杯奶茶钱"的代入感。

```
A flat-lay still life photograph, top-down view, on a warm wooden desk. A single white Xiaomi electric toothbrush lies horizontally. Next to it: a half-empty cup of milk tea with a paper straw, a small notebook, and a smartphone showing a secondhand marketplace app interface (blurred, generic). Warm natural window light from the right, soft shadow. Color palette: cream, light wood, soft white. Square 1:1 aspect ratio, lifestyle photography aesthetic, shallow depth of field. No text overlay, no watermark, no readable brand logo.
```

**关键控制点**：
- 1:1 正方形。
- 借"奶茶 + 牙刷"两个物件讲"奶茶钱"的价格锚，但完全无字。
- lifestyle 调性，适合周末发。

---

## #3 · 备选（科技感向）

**用途**：偏硬件审美，强调"参数党也能上"。

```
A clean product shot of a single white Xiaomi electric toothbrush standing upright on a matte black glossy surface, reflection visible. A subtle spotlight from above, dark gradient background. A small laser-engraved text "T302" visible on the toothbrush body. Composition: centered, minimalist, high-end tech aesthetic. Square 1:1 aspect ratio, studio lighting, photorealistic, 85mm lens. No overlay text, no watermark, no extra decoration.
```

**关键控制点**：
- 1:1 正方形。
- 黑色高光底 + 反射 = 数码博主标配视觉。
- "T302" 是型号字，英文+数字组合 AI 写起来比中文稳。

---

## 调度建议

- OpenClaw agent 读到本文件后，**默认用 #1** 调 `gemini-image`。
- 生成成功 → 保存为 `01_cover.png` 与本文件同目录。
- 生成失败 3 次 → 回退 #2，再失败 → #3，再失败 → 整篇 post_01 跳过本轮心跳。
- 生成结果**必须为 1:1 PNG 或 JPG**，分辨率 ≥ 1024×1024。
