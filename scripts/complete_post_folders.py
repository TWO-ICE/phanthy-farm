#!/usr/bin/env python3
"""
complete_post_folders.py — 对每个非"完"post 文件夹做"LLM 深度仿写 + 补素材 + 改名'完'"

【v3 规范】新工作流第二阶段：
  对每个 pending_posts/post_XX_<title>/ (不带"完"):
    1. 读 source.md（清洗后的公众号原文）
    2. 调 LLM 深度仿写 → content.md
       规则：删废话 / 保留结构 / 风格平移+场景化扩容 / 1500字+ / 无图 / 末尾溯源
    3. 匹配 JSON → 拿 item_id / pub_date / 图URL
    4. 下载 cover → reference.jpg (不裁剪，已存在跳过)
    5. 下载正文图 → img_1..N.jpg (裁 20% 去水印，应用 _lib 全部规则)
    6. 写 01_cover.prompt.md (图生图模板，JSON 格式)
    7. 写 manifest.json (含 cover_text + 完整 images 列表)
    8. 4 必含 + ≥1 张图都到位 → 文件夹改名加"完"

可重跑：已"完"跳过，已成型（v1 旧规范）跳过，单篇失败不阻断其他。
content.md 重新跑会覆盖（方便调 prompt 后批量重做）。

用法:
  python3 complete_post_folders.py --agent-slug xiaoyu-tech --json-dir ~/Downloads/小鱼科技v公众号文章 --count 3
  python3 complete_post_folders.py --agent-slug xiaoyu-tech --json-dir ~/Downloads/小鱼科技v公众号文章 --count 3 --dry-run
  python3 complete_post_folders.py --agent-slug xiaoyu-tech --json-dir ~/Downloads/小鱼科技v公众号文章 --all
"""
import argparse, json, os, re, sys, time
from pathlib import Path

# 把仓库 scripts/ + multi-agent-orchestrator/scripts/ 加到 sys.path 以便 import _lib + build_cover_prompt + writer
REPO = Path(os.environ.get("PHANTHY_REPO", "/Users/4paradigm/Documents/phanthy"))
sys.path.insert(0, str(REPO / 'scripts'))
# writer.py 在 multi-agent-orchestrator skill 里，优先放前面
sys.path.insert(0, str(Path(os.environ.get("HERMES_SKILLS", os.path.expanduser("~/.hermes/skills"))) / 'multi-agent-orchestrator' / 'scripts'))
import _lib  # noqa: E402
from build_cover_prompt import TEMPLATE as COVER_TEMPLATE  # noqa: E402
from writer import call_llm as _writer_call_llm  # noqa: E402  复用 multi-agent-orchestrator 的 LLM 调用


def call_llm(config, system_prompt, user_prompt, temperature=0.7, max_tokens=6000, retries=3):
    """
    LLM 调用（带 zhipu/glm 路由支持）
    - 解析 model name → (base_url, api_key, real_model)
    - zhipu 官方 API 不支持 OpenAI 的 "reasoning_content" 字段，需要特殊处理
    """
    import yaml as _yaml
    model = config['writer']['model']
    base_url, api_key, real_model = _resolve_model(model)

    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": real_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": 8000  # 给 reasoning 留空间，实际输出约 2000-3000
    }

    import requests, time as _time
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            print(f"  [LLM] {real_model} via {base_url} (第{attempt}次)", flush=True)
            resp = requests.post(url, headers=headers, json=payload, timeout=300)
            resp.raise_for_status()
            data = resp.json()
            msg = data['choices'][0]['message']
            content = msg.get('content', '')
            # GLM 系列 reasoning_content 字段不等于正文，只取 content
            if content and len(content.strip()) > 50:
                return content
            finish = data['choices'][0].get('finish_reason', '')
            print(f"  ⚠️ LLM返回空/极短响应(第{attempt}次) finish={finish}, content={len(content)}chars, reasoning={len(msg.get('reasoning_content',''))}chars", flush=True)
        except Exception as e:
            last_err = e
            print(f"  ⚠️ LLM调用失败(第{attempt}次): {e}", flush=True)

        if attempt < retries:
            _time.sleep(3 * attempt)

    if last_err:
        raise last_err
    raise RuntimeError(f"LLM连续{retries}次返回空响应")


def _resolve_model(model_name: str):
    """
    解析 model name → (base_url, api_key, real_model)
    支持：
      - glm-5.1, glm-5, z-ai/glm-5  → zhipu 官方
      - zhipu/glm-5.1, zhipu/glm-5  → 强制 zhipu 官方
      - phanthy/glm-5, phanthy/minimax-m2.5 → 走 phanthy 路由
      - 其他 → fallback 到 phanthy 路由
    """
    import yaml as _yaml
    import os as _os
    cfg_path = _os.path.expanduser("~/.hermes/config.yaml")
    cfg = {}
    if _os.path.isfile(cfg_path):
        with open(cfg_path) as f:
            cfg = _yaml.safe_load(f) or {}

    custom = {p.get("name"): p for p in cfg.get("custom_providers", [])}

    # 强制 zhipu
    if model_name.startswith("zhipu/") or model_name.lower() in ("glm-5", "glm-5.1", "glm-4", "glm-4.5", "glm-4.6", "glm-4.7"):
        real_model = model_name.split("/", 1)[-1] if "/" in model_name else model_name
        zp = custom.get("zhipu")
        if zp:
            return zp["base_url"], zp["api_key"], real_model
        return (_os.environ.get("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/coding/paas/v4"),
                _os.environ.get("ZHIPU_API_KEY", ""), real_model)

    # siliconflow（Pro/zai-org/GLM-4.7, Pro/zai-org/GLM-5, deepseek-ai/ 等）
    if model_name.startswith("Pro/") or model_name.startswith("deepseek-ai/") or "siliconflow" in model_name.lower():
        sf = custom.get("siliconflow")
        if sf:
            return sf["base_url"], sf["api_key"], model_name

    # 强制 phanthy 路由
    if model_name.startswith("phanthy/"):
        real_model = model_name.split("/", 1)[-1]
        ph = custom.get("phanthy")
        if ph:
            return ph["base_url"], ph["api_key"], real_model

    # 默认走 phanthy 路由
    ph = custom.get("phanthy")
    if ph:
        return ph["base_url"], ph["api_key"], model_name

    return ("https://router.phanthy.com/v1",
            _os.environ.get("OPENAI_API_KEY", ""), model_name)


# ==========================================
# LLM 深度仿写（你的需求：风格平移 + 场景化扩容 + 去废话 + 无图 + 末尾溯源）
# ==========================================

REWRITE_SYSTEM_PROMPT = """你是一位微信公众号的资深内容编辑，正在做"深度改写仿写"工作。

【核心目标】
将原文改写为风格相近但表达全新、字数更厚、符合公众号规范的"二创文章"。
绝对禁止原样照搬，必须彻底换表达方式。

【第一步：语料脱水（数据清洗）】
- 彻底扫描原文，**必须无条件删除所有干扰内容**：
  · "点亮关注、点赞收藏、转发、主页看更多、求个三连"等一切平台互动废话
  · "点击下方"、"看视频"、"扫码"等引导文案
  · 重复的口号、表情符号堆砌、无意义感叹（"！！！"连用、"家人们"等水词）
  · 任何与产品/知识干货无关的引流话术
- **干货一根毛都不删，废话一个字不留**

【第二步：骨架映射（保证结构 + 风格平移扩容）】
- **绝对严禁改变原文的叙事结构**：原文先说什么、后说什么、怎么总结，**洗稿后必须 1:1 映射**
- 在**完全保留原文笔风和逻辑**的前提下，对每个论点进行"场景化深度扩充"：
  · 补充底层原理（生理学/物理学/经济学/心理学）
  · 补充应用场景（实际使用中会遇到什么）
  · 补充对比参照（和同类动作/产品的横向对比）
  · 补充数字佐证（数据、参数、价格、年份）
- **风格保留**：保留原文的口语化、毒舌/调侃/严谨/朴实，**不要让每篇都长得像"科普教材"**。
  如果原文是毒舌调你就毒舌调，是朴实科普你就朴实科普，是案例叙事你就案例叙事。
- **不要套用固定模板**：不要每篇都用"## 标题 1 / ## 标题 2 / ## 标题 3"那种 AI 套路结构。
  原文章节怎么分的你就怎么分；原文不分小节你就别硬分。
- **死磕字数**：改写后字数**绝对不要低于 1500 字**，但**也不要超过 2200 字**（避免扩成水文）。
  如果原文较短（< 1000 字），必须通过场景化扩写把字数撑到 1500-2200 之间。
  如果原文已经 2000+ 字，**不要硬扩**，直接平移到 1500-2200 字范围即可。

【第三步：格式封装】
- 仿写后的内容输出为**纯文本 Markdown**
- 灵活运用 `#`、`##`、`###` 和 `**` `---` 做清爽排版（**根据原文需要，不是必须**）
- **严禁在 Markdown 内部嵌入任何图片链接**（绝对不要写 `![xxx](url)` 这样的标记）
- **绝对不要在文章开头、中间、或者除末尾以外的位置**写"原文链接"、"出处"、"来源"等
- 末尾**最后一行**统一加溯源（注意是**最后一行**，不是开头）：
  `> 💡 深度启发自：[{{原文标题}}]({{原文链接}})`
  （`{{原文标题}}` 和 `{{原文链接}}` 会在调用时由程序填入，你只需要在占位位置输出 `> 💡 深度启发自：[{title}]({url})`）

【4 层标记词（可选 · 不强制）】
- 4 层固定模板（观点/数据/案例/落地）**不强制使用**。
- 如果原文是数据型科普文，4 层结构**自然合适**就用。
- 如果原文是叙事型/案例型/答疑型，按原文骨架扩写，**不要硬塞 4 层**。
- 审计脚本不检查 4 层标记词，**只检查字数 ≥ 1500** 和 **末尾溯源链接**。

【直接输出】
直接输出改写后的文章正文（标题用 # 开头），不要输出任何说明、注释、JSON。
末尾溯源行由程序追加，你不要写这一行。
"""


REWRITE_USER_PROMPT_TEMPLATE = """## 原文标题（必须沿用，不要修改）
{title}

## 原文链接（用于末尾溯源，由程序自动追加，你不需要在文中任何位置写这个链接）
{orig_url}

## 原文正文（{char_count}字）
{body}

---

## 你的任务
将上面的原文深度改写为新文章。要求：
1. 完全删除所有平台互动废话（关注/点赞/三连/主页/扫码等），**干货一根毛不删**
2. **100% 保留原文叙事结构**（原文先说什么后说什么，必须 1:1 映射）
3. **保留原文笔风**（口语化/毒舌/朴实/严谨等，**不要写成"科普教材"**）
4. **场景化扩充**：对每个论点补充底层原理/应用场景/对比/数字佐证
5. **死磕字数 1500-2200**（不能少也不能多；原文短必须撑，原文长别硬扩）
6. **不要套用固定模板**：不要每篇都用"## 标题 1/2/3"那种 AI 套路，原文怎么分就怎么分
7. 不要写 `![](...)` 形式的图片标记
8. 不要在文中写"原文链接"、"出处"、"来源"等字样
9. 末尾溯源行（`> 💡 深度启发自：...`）由程序自动追加，你不需要写
10. **标题沿用原文**（不要改写标题，文件名需要和标题一致）

请开始输出改写后的文章正文（以 # 标题 开头，标题必须跟上面"原文标题"完全一致）。
"""


def rewrite_content(source_md_path: Path, title: str, orig_url: str,
                    model: str = "Pro/zai-org/GLM-4.7") -> dict:
    """
    调 LLM 深度仿写。
    Returns: {"ok": bool, "content": str, "char_count": int, "error": str}
    """
    # 读 source.md 拿正文（去标题行/封面图/原文链接）
    raw = source_md_path.read_text(encoding='utf-8')
    body = raw
    for pat in [r'^# .+\n', r'!\[封面图\]\([^)]+\)\n', r'> 原文链接：.+\n']:
        body = re.sub(pat, '', body, flags=re.M)
    body = body.strip()

    if len(body) < 200:
        return {"ok": False, "error": f"source.md 正文太短 ({len(body)}字)", "content": "", "char_count": 0}

    # 构造 config dict 适配 writer.call_llm 接口
    config = {
        "writer": {
            "model": model,
            "max_tokens": 8000,
            "temperature": 0.75,
        }
    }

    user_prompt = REWRITE_USER_PROMPT_TEMPLATE.format(
        title=title,
        orig_url=orig_url,
        char_count=len(body),
        body=body,
    )

    try:
        # max_tokens 8000: 2500字 ≈ 3500-5000 tokens（含 thinking buffer）
        text = call_llm(config, REWRITE_SYSTEM_PROMPT, user_prompt,
                        temperature=0.75, max_tokens=8000, retries=3)
    except Exception as e:
        return {"ok": False, "error": f"LLM 调用失败: {e}", "content": "", "char_count": 0}

    # 清理：去 markdown 包裹
    text = re.sub(r'^```\w*\n?', '', text.strip())
    text = re.sub(r'\n?```$', '', text)
    text = text.strip()

    # 清理：去掉 LLM 可能在文中加的"原文链接"等违规字样
    text = re.sub(r'>\s*原文链接[：:].*\n', '', text)
    text = re.sub(r'>\s*出处[：:].*\n', '', text)
    text = re.sub(r'>\s*来源[：:].*\n', '', text)

    # 清理：去掉所有 ![xxx](url) 图片标记
    text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)

    # 标题锁定：必须跟 source.md 标题一致（防止 LLM 改标题 → 文件夹名/manifest 标题混乱）
    lines = text.split('\n')
    if lines and lines[0].startswith('# '):
        llm_title = lines[0][2:].strip()
        if llm_title != title.strip():
            # 强制覆盖为 source.md 标题
            lines[0] = f'# {title.strip()}'
            text = '\n'.join(lines)

    # 末尾追加溯源行（统一格式）
    if orig_url:
        # 去末尾多余空行
        text = text.rstrip()
        # 追加"深度启发自"行（注意在 title 里替换占位符）
        source_line = f"\n\n> 💡 深度启发自：[{title.strip()}]({orig_url})\n"
        text = text + source_line

    char_count = len(text)

    return {"ok": True, "content": text, "char_count": char_count, "error": ""}


# ==========================================
# 文件/JSON 工具
# ==========================================

def find_json_for_title(json_dir: Path, title: str):
    """跟 init_post_folders 同款：精确匹配标题"""
    target = title.strip()
    for json_path in json_dir.glob('*.json'):
        try:
            raw = json.loads(json_path.read_text(encoding='utf-8'))
            art = _lib.unwrap_wemprss(raw)
            if art:
                art_title = (art.get('title') or '').strip()
                if art_title == target:
                    return art.get('id'), art
        except Exception:
            continue
    return None, None


def parse_source_md(md_path: Path):
    """从 source.md 提取：title, orig_url
    兼容两种格式：
      - > 原文链接：https://...  (清洗md原始)
      - > 💡 深度启发自：[标题](URL)  (init 阶段从 content.md rename 来的)
    """
    text = md_path.read_text(encoding='utf-8')
    title = orig_url = ''
    for line in text.split('\n'):
        if line.startswith('# ') and not title:
            title = line[2:].strip()
        # 清洗md原始格式
        m = re.match(r'> 原文链接：(.+)', line.strip())
        if m:
            orig_url = m.group(1).strip()
        # 兼容 init 把 content.md rename 为 source.md 的情况
        m2 = re.match(r'>\s*💡?\s*深度启发自.*?]\((https?://[^)]+)\)', line.strip())
        if m2 and not orig_url:
            orig_url = m2.group(1).strip()
    return title, orig_url


def get_aspect(pil_size) -> float:
    if not pil_size:
        return 1.0
    w, h = pil_size
    return round(w / h, 2) if h else 1.0


def build_cover_prompt_md(title: str, subtitle: str = '', price: str = '') -> str:
    import copy
    data = copy.deepcopy(COVER_TEMPLATE)
    data['text']['title']['content'] = title
    data['text']['subtitle']['content'] = subtitle
    data['text']['price_tag']['content'] = price
    content = (
        f"# 01_cover · 封面 Prompt（JSON 模板 · 策略 C:3:4 图生图 + 中文标题）\n\n"
        f"> 本文件是 **JSON 结构化模板**，agent 读取后填入占位符 → 调 gemini-image。\n"
        f"> **method**: 图生图，参考图 = `reference.jpg`\n"
        f"> **aspect_ratio**: 3:4 竖版（适配 phanthy 移动端 feed 卡片）\n"
        f"> **占位符**: `{{TITLE}}` / `{{SUBTITLE}}` / `{{PRICE}}` 已预填\n\n"
        f"```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```\n"
    )
    return content


def build_manifest(post_idx: str, title: str, item_id: str, orig_url: str,
                   pub_date: str, agent_slug: str,
                   cover_aspect: float, body_records: list) -> dict:
    images = [
        {
            'slot': 'reference',
            'kind': 'original',
            'file': 'reference.jpg',
            'source': 'wemprss_image_proxy',
            'source_rank': 'cover',
            'cdn_url': '',
            'aspect_ratio': cover_aspect,
            'note': '原文封面，作为图生图参考图',
        },
        {
            'slot': 'cover',
            'kind': 'ai_prompt',
            'prompt_file': '01_cover.prompt.md',
            'prompt_strategy': 'C',
            'cdn_url': '',
            'aspect_ratio': 0.75,
            'note': '1 推荐 prompt + 2 备选；龙虾农场默认调 gemini-image 用 #1 生成',
            'method': 'image_to_image',
        },
    ]
    for rec in body_records:
        images.append({
            'slot': f"body_{rec['rank']}",
            'kind': 'original',
            'file': rec['file'],
            'source': 'wemprss_image_proxy',
            'source_rank': rec['rank'],
            'cdn_url': '',
            'aspect_ratio': rec.get('aspect', 1.0),
        })

    return {
        'post_index': post_idx,
        'title': title,
        'source_item_id': item_id,
        'source_orig_url': orig_url,
        'source_pub_date': pub_date,
        'agent_slug': agent_slug,
        'content_md': 'content.md',
        'cover_text': {
            'title': title[:22],
            'subtitle': '',
            'price_tag': '行业速览',
        },
        'images': images,
    }


# ==========================================
# 主流程
# ==========================================

def is_post_complete(post_dir: Path) -> bool:
    """判断 post 是否真的'成型'：4 必含 + ≥1 张图都存在"""
    required = ['content.md', 'manifest.json', '01_cover.prompt.md', 'reference.jpg']
    if not all((post_dir / f).exists() for f in required):
        return False
    if not any(post_dir.glob('img_*.jpg')):
        return False
    return True


def complete_one(post_dir: Path, json_dir: Path, agent_slug: str,
                 force_rewrite: bool = False, model: str = "minimax/minimax-m2.5") -> dict:
    """完成一个 post 文件夹：LLM 仿写 + 补素材 + 改名'完'"""
    is_done = post_dir.name.endswith('完')
    if is_done:
        return {'ok': True, 'reason': 'already_done', 'skipped': True}

    # 跳过真正"已成型"的 post（4 必含 + 图都有 → v1 旧规范完整成稿）
    if is_post_complete(post_dir):
        return {'ok': True, 'reason': 'already_formed', 'skipped': True}

    # 1. 读 source.md
    src_path = post_dir / 'source.md'
    if not src_path.exists():
        return {'ok': False, 'reason': 'no_source_md'}

    # 清理脏 md
    for f in post_dir.glob('*.md'):
        if f.name not in ('source.md', 'content.md', '01_cover.prompt.md'):
            f.unlink(missing_ok=True)

    title, orig_url = parse_source_md(src_path)
    if not title:
        return {'ok': False, 'reason': 'no_title'}

    # 2. 调 LLM 深度仿写（除非已有 content.md 且不强制重写）
    content_path = post_dir / 'content.md'
    if not content_path.exists() or force_rewrite:
        print(f"    [LLM 仿写] {post_dir.name[:50]}...", flush=True)
        result = rewrite_content(src_path, title, orig_url, model=model)
        if not result['ok']:
            return {'ok': False, 'reason': f'rewrite_failed: {result["error"]}'}

        # 字数校验（必须 1500+，除非 source.md 本来就 1500 以下）
        if result['char_count'] < 1500:
            return {
                'ok': False,
                'reason': f'rewrite_too_short: {result["char_count"]}字 < 1500',
                'char_count': result['char_count'],
            }

        content_path.write_text(result['content'], encoding='utf-8')

    # 3. 匹配 JSON（如果之前已写过 content.md，item_id 可为 None，manifest 用占位）
    item_id, art = find_json_for_title(json_dir, title)
    if not art:
        # JSON 匹配失败：允许继续（content.md 已写好），用占位元数据
        print(f"    ⚠️  未匹配到 JSON（{title[:30]}），manifest 用占位元数据", flush=True)
        item_id = "unknown"
        pub_date = ""
        cover_url = ""
        content_html = ""
    else:
        from datetime import datetime
        pub_date_unix = art.get('publish_time', 0)
        pub_date = datetime.fromtimestamp(pub_date_unix).strftime('%Y-%m-%d') if pub_date_unix else ''
        cover_url = art.get('pic_url', '')
        content_html = (art.get('content_html') or '').strip()

    # 4. 下载 cover → reference.jpg（如有 cover_url）
    ref_path = post_dir / 'reference.jpg'
    if cover_url and not ref_path.exists():
        try:
            ok, msg = _lib.download_and_crop(cover_url, ref_path, crop_bottom=0.0)
            if not ok:
                print(f"    ⚠️  cover 下载失败: {msg}", flush=True)
        except Exception as e:
            print(f"    ⚠️  cover 下载异常: {e}", flush=True)
    # 没 cover_url 不阻断（content.md 已写好，后续补图）

    # 5. 下载正文图
    json_images = _lib.parse_image_urls_from_html(content_html)
    candidates = _lib.filter_candidates(json_images, cover_url)
    candidates = candidates[:12]

    seen_hashes = []
    body_records = []
    body_failed = 0
    for n, (score, pos, img) in enumerate(candidates, 1):
        dst = post_dir / f'img_{n}.jpg'
        if dst.exists():
            reason = _lib.post_download_filter(dst, seen_hashes)
            if not reason:
                from PIL import Image
                try:
                    im = Image.open(dst)
                    body_records.append({
                        'rank': n, 'file': f'img_{n}.jpg', 'url': img['url'],
                        'aspect': get_aspect(im.size),
                    })
                    continue
                except Exception:
                    pass
        try:
            ok, msg = _lib.download_and_crop(img['url'], dst, crop_bottom=_lib.CROP_BOTTOM)
            if not ok:
                body_failed += 1
                continue
            reason = _lib.post_download_filter(dst, seen_hashes)
            if reason:
                dst.unlink(missing_ok=True)
                body_failed += 1
                continue
            from PIL import Image
            im = Image.open(dst)
            body_records.append({
                'rank': n, 'file': f'img_{n}.jpg', 'url': img['url'],
                'aspect': get_aspect(im.size),
            })
        except Exception as e:
            body_failed += 1

    if not body_records:
        # 图全过滤掉：标"缺图"状态，保留 content.md（不删！便于以后补图或人工重跑）
        # 标记文件：MISSING_IMGS 防止 OpenClaw 误读为可发帖
        (post_dir / 'MISSING_IMGS').write_text(
            f'all_body_imgs_failed ({body_failed} tried) at {time.strftime("%Y-%m-%d %H:%M:%S")}\n'
            f'cover_url: {cover_url}\n'
            f'建议：\n'
            f'  - 放宽 _lib.post_download_filter 阈值后再跑 complete\n'
            f'  - 或人工挑选几张图放到 {post_dir}/img_1.jpg 后改"完"\n',
            encoding='utf-8'
        )
        return {'ok': False, 'reason': f'all_body_imgs_failed ({body_failed} tried) - marked missing_images', 'body_imgs': 0, 'body_failed': body_failed}

    # 6. 写 01_cover.prompt.md
    cover_prompt_path = post_dir / '01_cover.prompt.md'
    if not cover_prompt_path.exists():
        cover_prompt_path.write_text(build_cover_prompt_md(title), encoding='utf-8')

    # 7. 写 manifest.json
    m = re.match(r'^post_(\d+)_', post_dir.name)
    post_idx = m.group(1) if m else '00'
    cover_aspect = 1.0
    try:
        from PIL import Image
        cover_aspect = get_aspect(Image.open(ref_path).size)
    except Exception:
        pass

    manifest = build_manifest(
        post_idx=post_idx, title=title, item_id=item_id, orig_url=orig_url,
        pub_date=pub_date, agent_slug=agent_slug,
        cover_aspect=cover_aspect, body_records=body_records,
    )
    (post_dir / 'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8'
    )

    # 8. 4 必含 + ≥1 张图都到位 → 改名"完"
    have_all = all((post_dir / f).exists() for f in
                   ['content.md', 'manifest.json', '01_cover.prompt.md', 'reference.jpg'])
    have_img = any(post_dir.glob('img_*.jpg'))

    if have_all and have_img:
        new_name = post_dir.name + '完'
        new_path = post_dir.parent / new_name
        if not new_path.exists():
            post_dir.rename(new_path)
        return {
            'ok': True, 'reason': 'completed_and_marked_done',
            'new_name': new_name, 'body_imgs': len(body_records), 'body_failed': body_failed,
        }
    else:
        return {
            'ok': False, 'reason': f'incomplete (have_all={have_all}, have_img={have_img})',
            'body_imgs': len(body_records), 'body_failed': body_failed,
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--agent-slug', required=True)
    ap.add_argument('--json-dir', required=True, help='原始 JSON 目录')
    ap.add_argument('--count', type=int, default=0, help='要 complete 的篇数（0 = 全部）')
    ap.add_argument('--all', action='store_true', help='complete 全部非"完"post')
    ap.add_argument('--dry-run', action='store_true', help='只看会跑哪些，不真下载')
    ap.add_argument('--force-rewrite', action='store_true', help='强制重写 content.md（覆盖已有的）')
    ap.add_argument('--cleanup-orphans', action='store_true', help='清掉半成品（有 content.md 无 manifest 的）')
    ap.add_argument('--model', default='glm-4.7', help='LLM 模型（默认 GLM-4.7 走 zhipu 官方 API）')
    args = ap.parse_args()

    PENDING = REPO / 'agents' / args.agent_slug / 'pending_posts'
    JSON_DIR = Path(args.json_dir).expanduser()

    if not PENDING.exists():
        print(f'❌ pending_posts 不存在: {PENDING}', file=sys.stderr)
        sys.exit(1)
    if not JSON_DIR.exists():
        print(f'❌ JSON 目录不存在: {JSON_DIR}', file=sys.stderr)
        sys.exit(1)

    def numeric_key(name):
        m = re.match(r'^post_(\d+)_', name)
        return int(m.group(1)) if m else 0

    all_dirs = [d for d in PENDING.iterdir() if d.is_dir()]
    pending_dirs = []
    skipped_done = 0
    skipped_formed = 0
    cleanup_count = 0
    for d in all_dirs:
        if d.name.endswith('完'):
            skipped_done += 1
            continue
        # 半成品：有 content.md 但没 manifest → 清理
        if args.cleanup_orphans:
            if (d / 'content.md').exists() and not (d / 'manifest.json').exists():
                (d / 'content.md').unlink(missing_ok=True)
                cleanup_count += 1
                continue
        if is_post_complete(d):
            skipped_formed += 1
            continue
        pending_dirs.append(d)
    pending_dirs.sort(key=lambda d: (numeric_key(d.name), d.name))

    if not args.all and args.count > 0:
        pending_dirs = pending_dirs[:args.count]

    print(f'=== complete_post_folders.py ===')
    print(f'  agent:    {args.agent_slug}')
    print(f'  json_dir: {JSON_DIR}')
    print(f'  跳过 已完={skipped_done}, 已成型={skipped_formed}')
    if cleanup_count:
        print(f'  清理半成品: {cleanup_count} 个')
    print(f'  待 complete: {len(pending_dirs)} 个')
    if args.dry_run:
        print(f'  *** DRY-RUN: 不实际下载/调LLM ***')

    success = failed = 0
    for i, post_dir in enumerate(pending_dirs, 1):
        if args.dry_run:
            src_path = post_dir / 'source.md'
            if src_path.exists():
                title, _ = parse_source_md(src_path)
                print(f'  [{i}] {post_dir.name} | title={title[:30]}')
            else:
                print(f'  [{i}] {post_dir.name} | (无 source.md)')
            continue

        t0 = time.time()
        result = complete_one(post_dir, JSON_DIR, args.agent_slug,
                             force_rewrite=args.force_rewrite, model=args.model)
        # 并发保护：如果目录被其他进程改了"完"，跳过统计
        if not post_dir.exists():
            print(f"  ⚠️ 目录已被移除/改名，跳过: {post_dir.name}")
            continue
        elapsed = time.time() - t0

        if result.get('skipped'):
            continue
        if result['ok']:
            success += 1
            new_name = result.get('new_name', '?')
            imgs = result.get('body_imgs', 0)
            print(f'  ✅ [{i}/{len(pending_dirs)}] {post_dir.name} → {new_name} ({imgs} 图) [{elapsed:.1f}s]')
        else:
            failed += 1
            reason = result.get('reason', '?')
            print(f'  ❌ [{i}/{len(pending_dirs)}] {post_dir.name}: {reason} [{elapsed:.1f}s]', flush=True)

    if args.dry_run:
        print(f'\n[DRY-RUN 完成]')
        return

    print(f'\n[Done] 成功 {success}, 失败 {failed}')
    print(f'  输出: {PENDING}')


if __name__ == '__main__':
    main()
