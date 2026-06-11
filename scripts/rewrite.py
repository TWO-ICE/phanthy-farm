#!/usr/bin/env python3
"""
通用仿写脚本 v1.0

整合来源：
  1. salt_rewrite.py 的工程框架（LLM调用、分块、溯源行、retry）
  2. article-deslop 的方法论（骨架提取、7条仿写规则、去AI味）
  3. 通用仿写三步规则（语料脱水 → 骨架映射 → 格式封装）

字数策略：
  - 从 agent 的 TUNING.md 读取目标字数范围（默认 3500-4500）
  - 原文 > 6000字时分块仿写，否则整篇一次

工作方式：
  - 预处理（脱水+骨架提取）→ 仿写（整篇或分块）→ 去AI味 pass → 溯源行追加

用法：
  python3 rewrite.py --agent keji-xiansheng --count 5
  python3 rewrite.py --agent keji-xiansheng --folder "post_0001_..."
  python3 rewrite.py --agent keji-xiansheng --all --dry-run
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

REPO = Path(os.environ.get("PHANTHY_REPO", "/Users/4paradigm/Documents/phanthy"))
DESLOP_DIR = REPO / "article-deslop"

# ─── 模型配置 ───────────────────────────────────────────────
PROVIDERS = {
    "glm-4.7": {
        "base_url": "https://open.bigmodel.cn/api/coding/paas/v4",
        "api_key": "a74d59e68d9a45e68f477ff82402a9f9.LyIM3CAlZoYPE8Ii",
    },
    "MiniMax-M2.7": {
        "base_url": "https://api.minimaxi.com/v1",
        "api_key": "sk-cp-...xwJk",
    },
}
DEFAULT_MODEL = "glm-4.7"

# ─── 默认字数范围 ───────────────────────────────────────────────
DEFAULT_MIN_WORDS = 3500
DEFAULT_MAX_WORDS = 4500
CHUNK_THRESHOLD = 6000  # 原文超过此字数才分块


# ═══════════════════════════════════════════════════════════════
#  加载外部资源
# ═══════════════════════════════════════════════════════════════


def resolve_agent_dir(repo, agent_name):
    """自动匹配带序号的agent目录，如 onehu-zhihu → 01_onehu-zhihu"""
    agents_dir = os.path.join(repo, "agents")
    # 精确匹配
    if os.path.isdir(os.path.join(agents_dir, agent_name)):
        return os.path.join(agents_dir, agent_name)
    # 带序号匹配
    for d in os.listdir(agents_dir):
        if d.endswith("_" + agent_name) or d == agent_name:
            return os.path.join(agents_dir, d)
    return os.path.join(agents_dir, agent_name)

def load_banned_words():
    """加载禁用词表，返回（禁用词列表, 替换映射）"""
    banned_file = DESLOP_DIR / "references" / "banned-words.md"
    if not banned_file.exists():
        print("  ⚠️ 禁用词表不存在，跳过: " + str(banned_file))
        return [], {}

    text = banned_file.read_text(encoding="utf-8")
    words = []
    replacements = {}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("|") and not line.startswith("|---") and not line.startswith("| 禁用词"):
            parts = [p.strip() for p in line.split("|")]
            # parts: ['', '禁用词', '替换为/问题', '']
            if len(parts) >= 3:
                w = parts[1].strip()
                if w and not w.startswith("—"):
                    words.append(w)
                    r = parts[2].strip() if len(parts) > 2 else ""
                    if r and r not in ("—", "删", "删掉"):
                        replacements[w] = r
    return words, replacements


def load_rewrite_examples():
    """加载改写范例作为 few-shot"""
    examples_file = DESLOP_DIR / "references" / "rewrite-examples.md"
    if not examples_file.exists():
        print("  ⚠️ 改写范例不存在，跳过: " + str(examples_file))
        return ""
    return examples_file.read_text(encoding="utf-8")


def parse_tuning_md(tuning_path):
    """从 agent 的 TUNING.md 提取仿写参数

    返回 dict:
      min_words, max_words, style, model, chunk_enabled
    """
    result = {
        "min_words": DEFAULT_MIN_WORDS,
        "max_words": DEFAULT_MAX_WORDS,
        "style": "",
        "model": DEFAULT_MODEL,
        "chunk_enabled": None,  # None = 自动（按阈值）
    }

    if not os.path.exists(tuning_path):
        return result

    text = open(tuning_path, encoding="utf-8").read()

    # 提取字数范围 —— 支持 "3500-4500字"、"3500 - 4500" 等格式
    m = re.search(r'(\d[\d,]*)\s*[-~到至]\s*(\d[\d,]*)\s*字', text)
    if m:
        result["min_words"] = int(m.group(1).replace(",", ""))
        result["max_words"] = int(m.group(2).replace(",", ""))

    # 单独的字数基准线（如 onehu-zhihu 的 "12000字"）
    if not m:
        m2 = re.search(r'基准线[：:]\s*\*{0,2}(\d[\d,]*)\s*字', text)
        if m2:
            val = int(m2.group(1).replace(",", ""))
            result["min_words"] = val
            result["max_words"] = int(val * 1.1)

    # 提取模型
    m_model = re.search(r'主力模型[：:]\s*\*{0,2}(\S+?)\*{0,2}(?:\s|（|$)', text)
    if m_model:
        model_name = m_model.group(1).strip("*")
        if model_name in PROVIDERS:
            result["model"] = model_name

    # 提取风格描述
    m_style = re.search(r'风格[：:]\s*(.+)', text)
    if m_style:
        result["style"] = m_style.group(1).strip()

    # 提取扩容手法
    m_expand = re.search(r'扩容手法[：:]\s*(.+)', text)
    if m_expand:
        if result["style"]:
            result["style"] += "；" + m_expand.group(1).strip()
        else:
            result["style"] = m_expand.group(1).strip()

    # 骨架结构描述
    m_skeleton = re.search(r'骨架[：:]\s*(.+)', text)
    if m_skeleton:
        if result["style"]:
            result["style"] += "；结构：" + m_skeleton.group(1).strip()
        else:
            result["style"] = "结构：" + m_skeleton.group(1).strip()

    return result


# ═══════════════════════════════════════════════════════════════
#  LLM 调用
# ═══════════════════════════════════════════════════════════════

def resolve_api_key(model=None):
    """获取指定模型的 API key 和 base_url"""
    model = model or DEFAULT_MODEL
    if model not in PROVIDERS:
        raise RuntimeError(f"未知模型: {model}，可选: {list(PROVIDERS.keys())}")
    return PROVIDERS[model]["api_key"], PROVIDERS[model]["base_url"]


def call_llm(system_prompt, user_prompt, model=None, temperature=0.7, max_tokens=131072, retries=3):
    """调用 LLM API，支持多模型切换"""
    import requests

    model = model or DEFAULT_MODEL
    api_key, base_url = resolve_api_key(model)
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    # 智谱推理模型需要关闭 thinking
    if "bigmodel.cn" in base_url:
        payload["temperature"] = 1.0
        payload["max_tokens"] = 65536
        payload["thinking"] = {"type": "disabled"}

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            print(f"  [LLM] {model} attempt {attempt}/{retries}", flush=True)
            resp = requests.post(url, headers=headers, json=payload, timeout=600,
                                 proxies={"http": "", "https": ""})
            resp.raise_for_status()
            data = resp.json()
            msg = data['choices'][0]['message']
            content = msg.get('content', '')
            # MiniMax 等模型可能把思考过程输出到正文里，需要清理
            if content.startswith('<') or content.startswith('The user'):
                # 去掉开头的 thinking/thought 块
                content = re.sub(r'^<think.*?>.*?</think\s*>\s*', '', content, flags=re.DOTALL)
                content = re.sub(r'^<thought.*?>.*?</thought\s*>\s*', '', content, flags=re.DOTALL)
                # 如果没有标签但有英文思考文本，跳到第一个 # 标题
                if not content.strip().startswith('#') and '# ' in content:
                    idx = content.index('# ')
                    content = content[idx:]
            if content and len(content.strip()) > 100:
                return content
            finish = data['choices'][0].get('finish_reason', '')
            print(f"  ⚠️ Empty/short response (attempt {attempt}) finish={finish}, "
                  f"content={len(content)}chars", flush=True)
        except Exception as e:
            last_err = e
            print(f"  ⚠️ LLM call failed (attempt {attempt}): {e}", flush=True)

        if attempt < retries:
            time.sleep(5 * attempt)

    raise RuntimeError(f"LLM调用失败 {retries} 次: {last_err}")


# ═══════════════════════════════════════════════════════════════
#  文本处理
# ═══════════════════════════════════════════════════════════════

def split_into_chunks(text, chunk_size=3000):
    """按段落边界切分文本为块"""
    paragraphs = text.split('\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 1 > chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = para
        else:
            current_chunk = current_chunk + '\n' + para if current_chunk else para

    if current_chunk:
        chunks.append(current_chunk)

    # 如果最后一块太短(<500字)，合并到前一块
    if len(chunks) >= 2 and len(chunks[-1]) < 500:
        chunks[-2] = chunks[-2] + '\n' + chunks[-1]
        chunks.pop()

    return chunks


def extract_source_info(source_text):
    """从 source.md 提取标题、URL 和正文

    返回 (title, url, body)
    """
    # 提取标题
    title_match = re.match(r'^#\s+(.+)', source_text)
    title = title_match.group(1).strip() if title_match else ""

    # 提取原文链接（多种格式）
    url = ""
    # 格式1: > 原文链接：URL
    url_match = re.search(r'>\s*原文链接[：:]\s*(https?://\S+)', source_text)
    if url_match:
        url = url_match.group(1)
    # 格式2: > 深度启发自：[标题](URL)
    if not url:
        url_match2 = re.search(r'>\s*(?:深度)?启发自[：:]\s*\[.*?\]\((https?://\S+?)\)', source_text)
        if url_match2:
            url = url_match2.group(1)
    # 格式3: 纯URL行
    if not url:
        url_match3 = re.search(r'(https?://\S+)', source_text)
        if url_match3:
            url = url_match3.group(1)

    # 去掉标题行、原文链接行、溯源行，取正文
    body = source_text
    body = re.sub(r'^#\s+.+\n*', '', body, count=1)
    body = re.sub(r'>\s*原文链接[：:]\s*\S+\n*', '', body)
    body = re.sub(r'>\s*💡\s*深度启发自[：:]\s*\S+\n*', '', body)
    body = body.strip()

    return title, url, body


def dehydrate(text):
    """语料脱水：删除平台互动废话

    删除：关注/点赞/三连/引流话术/重复口号等
    保留：正文、对白、数据、论点
    """
    lines = text.split('\n')
    cleaned = []
    skip_patterns = [
        r'关注(公众号|作者|我|我们|不迷路)',
        r'点赞|三连|投币|收藏|转发',
        r'扫码|搜索.*关注|长按.*关注',
        r'(加|进)群|私信我|后台回复',
        r'更多精彩(内容|文章)',
        r'—+\s*/?\s*(BEGIN|END|MORE|ENDMORE)\s*/?\s*—+',
        r'点击(阅读|查看|原文|更多)',
        r'喜欢就.*点|觉得不错就',
        r'声明.*转载|版权声明',
        r'^\s*来源[：:]\s*$',
        r'微信公众号|公众号：|公众号ID',
    ]
    skip_re = re.compile('|'.join(skip_patterns), re.IGNORECASE)

    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned.append(line)
            continue
        # 跳过图片行
        if re.match(r'^!\[.*?\]\(.*?\)\s*$', stripped):
            continue
        # 跳过平台互动废话
        if skip_re.search(stripped):
            continue
        cleaned.append(line)

    # 合并多余空行
    result = re.sub(r'\n{3,}', '\n\n', '\n'.join(cleaned))
    return result.strip()


# ═══════════════════════════════════════════════════════════════
#  Prompt 构建
# ═══════════════════════════════════════════════════════════════

def build_system_prompt(tuning, banned_words, rewrite_examples):
    """构建仿写的 system prompt

    整合：
    - article-deslop 的三步方法论
    - 通用仿写三步规则
    - agent 的 TUNING.md 配置
    """
    style_section = ""
    if tuning["style"]:
        style_section = f"""

【风格要求（来自 agent 配置）】
{tuning['style']}
"""

    banned_section = ""
    if banned_words:
        # 只列核心禁用词（前60个），避免 prompt 过长
        display_words = banned_words[:60]
        banned_section = f"""

【禁用词（绝对不要在文章中出现）】
以下是AI味最重的词，出现任何一个都会让读者觉得是AI写的，必须完全避免：
{', '.join(display_words)}
{"...（共" + str(len(banned_words)) + "个，完整列表已加载用于检查）" if len(banned_words) > 60 else ""}
"""

    examples_section = ""
    if rewrite_examples:
        # 截取范例的关键部分（避免太长）
        examples_section = f"""

【改写范例（参考这些范例的改法）】
{rewrite_examples[:3000]}
"""

    prompt = f"""你是一位资深文字编辑，正在做「深度仿写」工作。

【核心目标】
将原文改写为风格相近、表达全新、字数达标的文章。
绝对禁止原样照搬，必须彻底换表达方式。
所有事实、数据、论点、来源必须 100% 保留，一个都不能少。

【第一步：语料脱水】
- 删除所有非正文内容：平台互动废话（关注/点赞/三连/引流话术）
- 保留全部正文内容、数据、论点、论据
- 删除 Markdown 图片链接 ![](url)

【第二步：骨架映射 + 风格平移 + 精准扩容】
先提取原文骨架（核心论点、关键事实、数据引用、人物事件、文章结构），然后仿写。

仿写7条规则：
1. **换开头**：如果原文用"大背景铺垫"开头（"近年来""随着…的发展""在…背景下"），必须换——用具体事实/数据/场景开头
2. **换连接方式**：不要每段都用连接词开头（"与此同时""然而""值得注意的是"），段落之间可以跳跃
3. **换表达方式**：每个句子都要用自己的话重说，事实不变
4. **换节奏**：段落长短交错，不要匀称；长句多拆短句；打散排比
5. **换态度表达**：不要假平衡，要有明确判断；立场和原文一致
6. **换结尾**：用具体事实/画面/反问收尾，不要升华/展望/总结
7. **加人味**：可以加口语化表达（"说白了""说实话"）、反问自嘲、具体化描述、适度调侃

仿写禁忌：
- 不要删掉原文的任何事实、数据、论点
- 不要添加原文没有的新论点、新数据
- 不要改变原文的核心结论和立场
- 不要把具体数字写模糊（"282.81亿元"不能写成"几百亿"）
- 不要把有来源的引用变无来源（"据XX报告"不能变"据调查"）
- 不要注水（排比叠词、重复强调、空洞过渡句）

【字数控制 —— 最重要】
- 目标字数：{tuning['min_words']} ~ {tuning['max_words']} 字
- 仿写后字数不得低于 {tuning['min_words']} 字
- 这是硬性要求，不是建议
{style_section}
{banned_section}
{examples_section}
【格式封装】
- 输出纯 Markdown
- 灵活运用 #、##、### 和 **、--- 做排版
- 严禁嵌入图片链接 ![](url)
- 不要在文章中写"原文链接""出处""来源"等
- 不要写溯源行（由程序追加）
- 直接输出改写后的文章正文（标题用 # 开头），不要输出任何说明、注释、JSON
"""

    return prompt


def build_chunk_prompt(chunk_idx, total_chunks, target_ratio):
    """构建分块仿写的 system prompt"""
    return f"""你是资深文字编辑，正在做「深度仿写」的分块处理。

现在你收到的是原文的第 {chunk_idx}/{total_chunks} 块。

【改写要求】
1. 彻底换表达方式，禁止原样照搬
2. 100% 保留原文的事实、数据、论点
3. 段落长短交错，不要匀称排比
4. 不要用"与此同时""值得注意的是""由此可见"等AI味连接词

【字数要求】
这一块改写后字数约为原文的 {target_ratio}。
严格遵守，不要超出太多，也不要缩水。

不要加标题，不要加溯源行，直接输出正文。"""


def build_deslop_prompt(banned_words):
    """构建去AI味的最终 pass prompt"""
    banned_list = ", ".join(banned_words[:80]) if banned_words else "（无禁用词表）"

    return f"""你是去AI味专家。你的任务是检查并修改一篇文章，消除所有AI写作的痕迹。

【检查清单】
1. **禁用词扫描**：以下词语绝对不能出现在文章中，出现任何一个都必须替换或删除：
{banned_list}

2. **节奏检查**：
   - 段落长短是否有变化？连续3个以上长度相近的段落打散
   - 有没有连续3句以上的排比？拆散
   - 有没有每段开头都用连接词？删掉多余的

3. **结尾检查**：
   - 结尾是事实/画面收尾，还是又升华了？
   - 有没有"这不仅关乎…更关乎…""让我们…"之类的尾巴？

4. **内容完整性**：
   - 不要删减任何事实、数据、论点
   - 只改表达方式，不改内容

【输出】
直接输出修改后的完整文章。不要输出修改说明、对比、注释。"""


# ═══════════════════════════════════════════════════════════════
#  核心仿写流程
# ═══════════════════════════════════════════════════════════════

def rewrite_folder(agent_path, folder_name, tuning, model=None, dry_run=False,
                    skip_deslop=False):
    """仿写单个文件夹

    返回 True=成功, False=跳过
    """
    # 兼容两种目录结构：
    # 结构A（盐选）: draft/folder_name/source.md（folder_name是目录）
    # 结构B（通用）: draft/folder_name.md（folder_name是文件）
    draft_dir = os.path.join(agent_path, "draft")
    post_dir = os.path.join(agent_path, "post")

    # 尝试结构A
    source_file_a = os.path.join(draft_dir, folder_name, "source.md")
    # 尝试结构B：draft文件本身就是 .md
    source_file_b = os.path.join(draft_dir, folder_name) if folder_name.endswith(".md") else None
    # 也尝试不带子目录的：draft/folder_name（可能文件夹名就是文件名）
    source_file_c = os.path.join(draft_dir, folder_name)

    source_file = None
    output_dir = os.path.join(post_dir, folder_name)  # 默认值
    if os.path.isfile(source_file_a):
        source_file = source_file_a
        output_dir = os.path.join(post_dir, folder_name)
    elif source_file_b and os.path.isfile(source_file_b):
        source_file = source_file_b
        # post 目录用去掉 .md 后的名字
        output_dir = os.path.join(post_dir, os.path.splitext(folder_name)[0])
    elif os.path.isfile(source_file_c):
        source_file = source_file_c
        output_dir = os.path.join(post_dir, os.path.splitext(folder_name)[0])

    if not source_file:
        # 最后尝试：folder_name 是目录但 source.md 不在其中
        print(f"  ⚠️ source 文件不存在，跳过: {folder_name}")
        return False

    output_file = os.path.join(output_dir, "content.md")

    # 如果已有成品且字数足够，跳过
    if os.path.exists(output_file):
        existing = open(output_file, encoding="utf-8").read()
        if len(existing) > tuning["min_words"] * 0.8:
            print(f"  ⏭️ 已有成品({len(existing)}字)，跳过: {folder_name}")
            return True

    source_text = open(source_file, encoding="utf-8").read()

    # 提取标题、URL、正文
    title, orig_url, body = extract_source_info(source_text)
    if not title:
        title = folder_name
        # 尝试从文件夹名提取标题
        m = re.match(r'post_\d+[_\s]*(.+?)(?:\.md)?$', folder_name)
        if m:
            title = m.group(1).strip()

    # 语料脱水
    clean_body = dehydrate(body)
    orig_len = len(clean_body)

    print(f"\n{'='*60}")
    print(f"📝 {folder_name}")
    print(f"   标题: {title}")
    print(f"   原文字数: {len(body)}  脱水后: {orig_len}")
    print(f"   目标字数: {tuning['min_words']} ~ {tuning['max_words']}")

    if dry_run:
        print(f"   [DRY RUN] 跳过实际仿写")
        return True

    # 加载资源
    banned_words, _ = load_banned_words()
    rewrite_examples = load_rewrite_examples()

    # 构建 system prompt
    sys_prompt = build_system_prompt(tuning, banned_words, rewrite_examples)

    # 决定是否分块
    should_chunk = (tuning["chunk_enabled"] is True) or \
                   (tuning["chunk_enabled"] is None and orig_len > CHUNK_THRESHOLD)

    if should_chunk and orig_len > CHUNK_THRESHOLD:
        # ── 分块仿写 ──
        chunks = split_into_chunks(clean_body, chunk_size=3000)
        print(f"   分块数: {len(chunks)} (块大小: {[len(c) for c in chunks]})")

        total_chunk_chars = sum(len(c) for c in chunks)
        target_ratio = tuning["min_words"] / total_chunk_chars if total_chunk_chars > 0 else 1.5
        # 限制扩写倍率，避免过度膨胀
        target_ratio = min(target_ratio, 3.0)

        rewritten_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_idx = i + 1
            print(f"\n  📦 块 {chunk_idx}/{len(chunks)} ({len(chunk)}字)...")

            chunk_sys = build_chunk_prompt(
                chunk_idx=chunk_idx,
                total_chunks=len(chunks),
                target_ratio=f"×{target_ratio:.1f}（即约{int(len(chunk)*target_ratio)}字）"
            )
            user_prompt = f"## 原文第{chunk_idx}块\n\n{chunk}"

            result = call_llm(chunk_sys, user_prompt, model=model,
                              temperature=0.7, max_tokens=131072)
            rewritten_chunks.append(result)
            print(f"     → 输出 {len(result)}字")

        # 拼接
        merged = '\n\n'.join(rewritten_chunks)
        print(f"\n  📊 拼接后总字数: {len(merged)}")

        # 如果字数不够，做一次整体扩写
        if len(merged) < tuning["min_words"]:
            print(f"  ⚠️ 字数不足({len(merged)} < {tuning['min_words']})，做整体扩写...")
            expand_prompt = f"""下面是一篇已改写的文章（{len(merged)}字），但字数不够。
目标字数: {tuning['min_words']}字。

请在保留现有内容的基础上，通过以下方式扩写：
1. 补充论点之间的过渡和因果链条（最重要）
2. 补充具体案例、数据解读、行业背景
3. 补充人物/事件的具体细节
4. 用口语化表达和具体场景让内容更丰满

【不要做】
- 不要堆砌环境描写和景物描写
- 不要重复强调已经说过的观点
- 不要用排比叠词注水
- 不要删除任何现有内容，只做加法

直接输出完整文章。

{merged}"""
            merged = call_llm(sys_prompt, expand_prompt, model=model,
                              temperature=0.6, max_tokens=131072)
            print(f"  📊 扩写后总字数: {len(merged)}")

        # 最终润色（消除拼接痕迹）
        if len(chunks) > 1:
            print(f"  ✨ 最终润色（消除拼接痕迹）...")
            merge_prompt = f"""你收到了一篇由 {len(chunks)} 块分别改写后拼接而成的文章。
请做最终通读润色：
1. 检查块与块之间的衔接是否自然，消除拼接痕迹
2. 确保人物称呼、时间线、数据前后一致
3. 不要删减内容，只做衔接润色
4. 不要加溯源行
5. 直接输出完整文章
"""
            merged = call_llm(merge_prompt, merged, model=model,
                              temperature=0.5, max_tokens=131072)
            print(f"  📊 润色后总字数: {len(merged)}")

    else:
        # ── 整篇一次仿写 ──
        print(f"   整篇仿写（原文{orig_len}字 ≤ {CHUNK_THRESHOLD}阈值）...")
        user_prompt = f"## 原文\n\n{clean_body}"
        merged = call_llm(sys_prompt, user_prompt, model=model,
                          temperature=0.7, max_tokens=131072)
        print(f"  📊 仿写后字数: {len(merged)}")

        # 如果字数不够，扩写一次
        if len(merged) < tuning["min_words"]:
            print(f"  ⚠️ 字数不足({len(merged)} < {tuning['min_words']})，做扩写...")
            expand_prompt = f"""下面是一篇已改写的文章（{len(merged)}字），但字数不够。
目标字数: {tuning['min_words']}字。

请在保留现有内容的基础上扩写：
1. 补充论点之间的过渡和因果链条
2. 补充具体案例、数据解读
3. 用口语化表达让内容更丰满

不要注水，不要删除现有内容。直接输出完整文章。

{merged}"""
            merged = call_llm(sys_prompt, expand_prompt, model=model,
                              temperature=0.6, max_tokens=131072)
            print(f"  📊 扩写后字数: {len(merged)}")

    # 清理分块残留：去掉孤立编号标题（如 "# 1"、"# 2"）
    merged = re.sub(r'\n#\s+\d{1,2}\s*\n', '\n', merged)

    # ── 去 AI 味 pass ──
    if not skip_deslop and banned_words:
        print(f"  🧹 去AI味最终 pass...")
        deslop_sys = build_deslop_prompt(banned_words)
        merged = call_llm(deslop_sys, merged, model=model,
                          temperature=0.5, max_tokens=131072)
        print(f"  📊 去AI味后字数: {len(merged)}")

    # ── 组装最终成品 ──
    # 确保有标题行
    if not merged.strip().startswith('#'):
        merged = f"# {title}\n\n{merged}"

    # 追加溯源行（从原文提取真实链接，不让LLM编）
    attribution = ""
    if orig_url:
        attribution = f"\n\n> 💡 深度启发自：[{title}]({orig_url})"
    elif title:
        attribution = f"\n\n> 💡 深度启发自：{title}"

    final = f"{merged.strip()}{attribution}"

    # 写入
    os.makedirs(output_dir, exist_ok=True)
    with open(output_file, 'w', encoding="utf-8") as f:
        f.write(final)

    # 字数校验
    final_chars = len(merged)
    pct = (final_chars / orig_len * 100) if orig_len > 0 else 0
    in_range = tuning["min_words"] <= final_chars <= tuning["max_words"]
    status = "✅" if in_range else ("⚠️" if final_chars < tuning["min_words"] else "📊")
    print(f"\n  {status} 完成！原始{orig_len} → 仿写{final_chars} ({pct:.0f}%)")
    if final_chars < tuning["min_words"]:
        print(f"     ⚠️ 未达目标字数 {tuning['min_words']}")
    elif final_chars > tuning["max_words"]:
        print(f"     📊 超出目标字数 {tuning['max_words']}（但只看下限，不截断）")

    return True


# ═══════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════

def discover_folders(agent_path):
    """列出 draft 目录下的所有待处理文件夹/文件

    支持两种结构：
    A. draft/post_XXXX_标题/source.md（子目录模式）
    B. draft/post_XXXX_标题.md（文件模式）
    """
    draft_dir = os.path.join(agent_path, "draft")
    if not os.path.isdir(draft_dir):
        return []

    folders = []
    for entry in sorted(os.listdir(draft_dir)):
        entry_path = os.path.join(draft_dir, entry)
        if os.path.isdir(entry_path):
            # 子目录模式：检查是否有 source.md
            if os.path.isfile(os.path.join(entry_path, "source.md")):
                folders.append(entry)
        elif entry.endswith(".md"):
            # 文件模式
            folders.append(entry)

    return folders


def main():
    parser = argparse.ArgumentParser(
        description="通用仿写脚本（整合 article-deslop 方法论）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python3 rewrite.py --agent keji-xiansheng --count 5
  python3 rewrite.py --agent keji-xiansheng --folder "post_0001_..."
  python3 rewrite.py --agent keji-xiansheng --all --dry-run
  python3 rewrite.py --agent keji-xiansheng --all --skip-deslop
        """
    )
    parser.add_argument("--agent", required=True, help="Agent slug (e.g. keji-xiansheng)")
    parser.add_argument("--model", default=None,
                        help=f"模型 (默认从 TUNING.md 读取，可选: {list(PROVIDERS.keys())})")
    parser.add_argument("--count", type=int, help="仿写篇数")
    parser.add_argument("--folder", help="指定单个文件夹名")
    parser.add_argument("--all", action="store_true", help="仿写所有未完成的")
    parser.add_argument("--dry-run", action="store_true", help="只看不写")
    parser.add_argument("--skip-deslop", action="store_true",
                        help="跳过去AI味最终 pass（节省一次LLM调用）")
    args = parser.parse_args()

    agent_path = resolve_agent_dir(REPO, args.agent)
    draft_dir = os.path.join(agent_path, "draft")

    if not os.path.isdir(draft_dir):
        print(f"❌ draft目录不存在: {draft_dir}")
        sys.exit(1)

    # 读取 agent 的 TUNING.md
    tuning_path = os.path.join(agent_path, "TUNING.md")
    tuning = parse_tuning_md(tuning_path)
    print(f"📋 Agent: {args.agent}")
    print(f"   目标字数: {tuning['min_words']} ~ {tuning['max_words']}")
    print(f"   模型: {tuning['model']}")

    # 确定模型
    model = args.model or tuning["model"]

    # 确定要处理的文件夹列表
    if args.folder:
        folders = [args.folder]
    else:
        all_folders = discover_folders(agent_path)
        # 过滤出还没有成品的
        folders = []
        for f in all_folders:
            # 判断输出路径
            if os.path.isdir(os.path.join(draft_dir, f)):
                post_content = os.path.join(agent_path, "post", f, "content.md")
            else:
                post_content = os.path.join(agent_path, "post", os.path.splitext(f)[0], "content.md")

            if not os.path.exists(post_content) or \
               len(open(post_content, encoding="utf-8").read()) < tuning["min_words"] * 0.8:
                folders.append(f)

        if args.count:
            folders = folders[:args.count]
        elif not args.all:
            print(f"❌ 请指定 --count N 或 --all 或 --folder XXX")
            sys.exit(1)

    print(f"🚀 通用仿写 - {args.agent} (模型: {model})")
    print(f"   待处理: {len(folders)} 篇")
    if args.dry_run:
        print(f"   [DRY RUN]")
    if args.skip_deslop:
        print(f"   [跳过去AI味 pass]")

    success = 0
    fail = 0
    for folder in folders:
        try:
            if rewrite_folder(agent_path, folder, tuning, model=model,
                              dry_run=args.dry_run, skip_deslop=args.skip_deslop):
                success += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            import traceback
            traceback.print_exc()
            fail += 1

    print(f"\n{'='*60}")
    print(f"🏁 完成！成功 {success}，失败 {fail}")


if __name__ == "__main__":
    main()
