#!/usr/bin/env python3
"""
盐选小说深度仿写脚本 v1.0

字数策略：
  - 原文 < 12000字 → 扩写到 12000字
  - 原文 ≥ 12000字 → 仿写后字数不超过原文 ±10%

工作方式：
  - 分块（每块≤3000字，按段落边界切）→ 逐块LLM改写 → 拼接 → 字数校验
  - 支持单篇和批量

用法：
  python3 salt_rewrite.py --agent onehu-zhihu --count 5
  python3 salt_rewrite.py --agent onehu-zhihu --folder "post_2081_..."
  python3 salt_rewrite.py --agent onehu-zhihu --all --dry-run
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

REPO = Path(os.environ.get("PHANTHY_REPO", "/Users/4paradigm/Documents/phanthy"))

# ─── 配置 ───────────────────────────────────────────────
PROVIDERS = {
    "glm-4.7": {
        "base_url": "https://open.bigmodel.cn/api/coding/paas/v4",
        "api_key": "bc4d14f45c094a5a98aa7bf4b43487e0.B34VTroSdq4zFG4e",
    },
    "MiniMax-M2.7": {
        "base_url": "https://api.minimaxi.com/v1",
        "api_key": "sk-cp-pgQCZv3bvTkW6XZCp2scPjR2xcP7CVQ8SpIOQeT-1RhSn9whPNFP7Anu98-1CKotAfcMXMLPkzrQno8bpa79vtR2RfQeWvD0jADiS714ww5v_D3hqHMxwJk",
    },
}
DEFAULT_MODEL = "glm-4.7"



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

def resolve_api_key(model=None):
    """获取指定模型的 API key 和 base_url"""
    model = model or DEFAULT_MODEL
    if model not in PROVIDERS:
        raise RuntimeError(f"未知模型: {model}，可选: {list(PROVIDERS.keys())}")
    return PROVIDERS[model]["api_key"], PROVIDERS[model]["base_url"]


SYSTEM_PROMPT = """你是一位知乎盐选小说的资深编辑，正在做「深度仿写」工作。

【核心目标】
将原文（盐选小说/故事）改写为风格相近、表达全新、字数达标的「二创文章」。
绝对禁止原样照搬，必须彻底换表达方式。

【第一步：语料脱水】
- 删除所有非正文内容：平台互动废话（关注/点赞/三连）、引流话术、重复口号
- **故事情节、人物对白、场景描写一根毛都不删**
- 保留原文所有情节转折和伏笔

【第二步：骨架映射 + 风格平移 + 精准扩容】
- **绝对严禁改变原文的叙事结构**：原文先说什么、后说什么、怎么收尾，仿写后必须 1:1 映射
- 在完全保留原文笔风和逻辑的前提下，对每个情节/场景进行「精准扩充」：
  · 【重点扩】情节转折的铺垫与过渡、因果逻辑链的补全、悬念的层层推进
  · 【适度扩】人物心理变化过程、对话潜台词（弦外之音）、关键动作的细节刻画
  · 【克制扩】环境描写（光影/声音/气味），每个场景最多2-3句，点到为止
- **风格保留**：保留原文的叙事口吻——是悬疑紧凑、温馨治愈、辛辣讽刺、还是冷静白描，原文什么味你什么味
- **不要套用固定模板**：原文怎么分段你就怎么分段，原文不分章节你就别硬分
- **禁止注水**：不要用排比叠词充字数，不要重复强调同一观点，不要加空洞过渡句

【第三步：字数控制 —— 最重要】
- 如果原文总字数 < 12000字：仿写后必须 ≥ 12000字，通过场景化扩写补足
- 如果原文总字数 ≥ 12000字：仿写后字数不得低于原文的90%，也不得超过原文的110%
- 这是硬性要求，不是建议

【第四步：格式封装】
- 输出纯文本 Markdown
- 灵活运用 #、##、### 和 **、--- 做清爽排版（根据原文需要，不是必须）
- 严禁在 Markdown 内部嵌入任何图片链接（绝对不要写 ![xxx](url)）
- 绝对不要在文章开头、中间写"原文链接"、"出处"、"来源"等
- 末尾最后一行：`> 💡 深度启发自：[{title}]({url})`（由程序追加，你不需要写）

【直接输出】
直接输出改写后的文章正文（标题用 # 开头），不要输出任何说明、注释、JSON。
"""

CHUNK_SYSTEM_PROMPT = """你是一位知乎盐选小说的资深编辑，正在做「深度仿写」工作。

现在你收到的是原文的第 {chunk_idx}/{total_chunks} 块。

【改写要求】
1. 彻底换表达方式，禁止原样照搬
2. 100% 保留原文的情节、对白含义、叙事节奏
3. 保留原文笔风（悬疑/温馨/讽刺/白描等）

【扩写方向 —— 按优先级排列】
优先级1（重点扩）：情节转折的铺垫与过渡、因果逻辑链的补全、悬念的层层推进
优先级2（适度扩）：人物心理变化过程、对话中的潜台词与弦外之音、关键动作的细节刻画
优先级3（克制用）：环境描写（光影/声音/气味），每个场景最多2-3句，点到为止，不要堆砌

【扩写禁忌】
- 不要对纯环境描写（天气/景色/建筑外观）做大幅扩写，原文几句你就几句
- 不要重复强调同一个观点或情绪，说一次就够了
- 不要用排比、叠词等修辞手法来注水
- 不要在段落之间加"不仅如此"、"更令人震惊的是"这类空洞过渡句

【字数要求】
这一块改写后字数约为原文的 {target_ratio}。
严格遵守，不要超出太多，也不要缩水。

不要加标题，不要加溯源行，直接输出正文。
"""

FINAL_MERGE_PROMPT = """你收到了一篇由 {total_chunks} 块分别改写后拼接而成的文章。
请做最终通读润色：
1. 检查块与块之间的衔接是否自然，消除拼接痕迹
2. 确保人物称呼、时间线、场景描述前后一致
3. 不要删减内容，只做衔接润色
4. 不要加溯源行
5. 直接输出完整文章
"""


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
                import re
                # 去掉 <think...</think?> 或 <thought...</thought> 标签
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
            err_body = resp.text[:200] if hasattr(resp, 'text') else ''
            print(f"  ⚠️ LLM call failed (attempt {attempt}): {e} | body: {err_body}", flush=True)

        if attempt < retries:
            time.sleep(5 * attempt)

    raise RuntimeError(f"LLM调用失败 {retries} 次: {last_err}")


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


def rewrite_folder(agent_path, folder_name, model=None, dry_run=False):
    """仿写单个文件夹"""
    draft_dir = os.path.join(agent_path, "draft", folder_name)
    post_dir = os.path.join(agent_path, "post", folder_name)
    source_file = os.path.join(draft_dir, "source.md")
    output_file = os.path.join(post_dir, "content.md")
    
    if not os.path.exists(source_file):
        print(f"  ⚠️ source.md 不存在，跳过: {folder_name}")
        return False
    
    # 如果已有成品，跳过
    if os.path.exists(output_file):
        existing = open(output_file).read()
        if len(existing) > 5000:
            print(f"  ⏭️ 已有成品({len(existing)}字)，跳过: {folder_name}")
            return True
    
    source_text = open(source_file).read()
    orig_len = len(source_text)
    
    # 提取标题和URL
    title_match = re.match(r'^#\s+(.+)', source_text)
    title = title_match.group(1).strip() if title_match else folder_name
    
    url_match = re.search(r'>\s*原文链接[：:]\s*(https?://\S+)', source_text)
    orig_url = url_match.group(1) if url_match else ""
    
    # 去掉标题行和原文链接行，取正文
    body = source_text
    body = re.sub(r'^#\s+.+\n*', '', body, count=1)
    body = re.sub(r'>\s*原文链接[：:]\s*\S+\n*', '', body)
    body = body.strip()
    
    print(f"\n{'='*60}")
    print(f"📝 {folder_name}")
    print(f"   标题: {title}")
    print(f"   原文字数: {orig_len}  正文: {len(body)}")
    
    # 字数目标
    target_min = max(12000, int(orig_len * 0.9))
    target_max = int(orig_len * 1.1) if orig_len >= 12000 else 15000
    print(f"   目标字数: {target_min} ~ {target_max}")
    
    if dry_run:
        print(f"   [DRY RUN] 跳过实际仿写")
        return True
    
    # 分块
    chunks = split_into_chunks(body, chunk_size=3000)
    print(f"   分块数: {len(chunks)} (块大小: {[len(c) for c in chunks]})")
    
    # 计算每块的目标字数比例
    total_chunk_chars = sum(len(c) for c in chunks)
    target_total = target_min  # 至少达到这个
    target_ratio = target_total / total_chunk_chars if total_chunk_chars > 0 else 1.5
    
    # 逐块改写
    rewritten_chunks = []
    for i, chunk in enumerate(chunks):
        chunk_idx = i + 1
        print(f"\n  📦 块 {chunk_idx}/{len(chunks)} ({len(chunk)}字)...")
        
        sys_prompt = CHUNK_SYSTEM_PROMPT.format(
            chunk_idx=chunk_idx,
            total_chunks=len(chunks),
            target_ratio=f"×{target_ratio:.1f}（即约{int(len(chunk)*target_ratio)}字）"
        )
        
        user_prompt = f"## 原文第{chunk_idx}块\n\n{chunk}"
        
        result = call_llm(sys_prompt, user_prompt, model=model, temperature=0.7, max_tokens=131072)
        rewritten_chunks.append(result)
        print(f"     → 输出 {len(result)}字")
    
    # 拼接
    merged = '\n\n'.join(rewritten_chunks)
    print(f"\n  📊 拼接后总字数: {len(merged)}")
    
    # 如果字数不够，做一次整体扩写
    if len(merged) < target_min:
        print(f"  ⚠️ 字数不足({len(merged)} < {target_min})，做整体扩写...")
        # 把拼接结果再喂给LLM做扩写
        expand_prompt = f"""下面是一篇已改写的文章（{len(merged)}字），但字数不够。
目标字数: {target_min}字。

请在保留现有内容的基础上，通过以下方式扩写：
1. 补充情节转折之间的铺垫与过渡（最重要）
2. 补充人物心理变化的过程和内心独白
3. 补充对话中的潜台词和言外之意
4. 补充关键动作和表情的细节刻画

【不要做】
- 不要堆砌环境描写和景物描写
- 不要重复强调已经说过的观点
- 不要用排比叠词注水
- 不要删除任何现有内容，只做加法

直接输出完整文章。

{merged}"""
        merged = call_llm(SYSTEM_PROMPT, expand_prompt, model=model, temperature=0.6, max_tokens=131072)
        print(f"  📊 扩写后总字数: {len(merged)}")
    
    # 最终润色（合并拼接痕迹）
    if len(chunks) > 1:
        print(f"  ✨ 最终润色（消除拼接痕迹）...")
        merge_prompt = FINAL_MERGE_PROMPT.format(total_chunks=len(chunks))
        try:
            merged = call_llm(merge_prompt, merged, model=model, temperature=0.5, max_tokens=131072)
            print(f"  📊 润色后总字数: {len(merged)}")
        except Exception as e:
            print(f"  ⚠️ 润色失败（{e}），使用拼接结果直接输出")
            print(f"  📊 拼接总字数: {len(merged)}")
    
    # 清理分块残留：去掉标题后紧跟的孤立编号标题（如 "# 1"、"# 2"）
    merged = re.sub(r'\n#\s+\d{1,2}\s*\n', '\n', merged)

    # 组装最终成品
    final = f"# {title}\n\n{merged}\n\n> 💡 深度启发自：[{title}]({orig_url})"
    
    # 写入
    os.makedirs(post_dir, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(final)
    
    # 字数校验
    final_chars = len(merged)
    pct = (final_chars / orig_len * 100) if orig_len > 0 else 0
    status = "✅" if target_min <= final_chars <= target_max else "⚠️"
    print(f"\n  {status} 完成！原始{orig_len} → 仿写{final_chars} ({pct:.0f}%)")
    if final_chars < target_min:
        print(f"     ⚠️ 未达目标字数 {target_min}")
    elif final_chars > target_max:
        print(f"     ⚠️ 超出目标字数 {target_max}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="盐选小说深度仿写")
    parser.add_argument("--agent", required=True, help="Agent slug (e.g. onehu-zhihu)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"模型 (默认: {DEFAULT_MODEL}, 可选: {list(PROVIDERS.keys())})")
    parser.add_argument("--count", type=int, help="仿写篇数")
    parser.add_argument("--folder", help="指定单个文件夹名")
    parser.add_argument("--all", action="store_true", help="仿写所有未完成的")
    parser.add_argument("--dry-run", action="store_true", help="只看不写")
    args = parser.parse_args()
    
    agent_path = resolve_agent_dir(REPO, args.agent)
    draft_dir = os.path.join(agent_path, "draft")
    
    if not os.path.isdir(draft_dir):
        print(f"❌ draft目录不存在: {draft_dir}")
        sys.exit(1)
    
    # 确定要处理的文件夹列表
    if args.folder:
        folders = [args.folder]
    else:
        # 列出所有draft文件夹
        all_folders = sorted(os.listdir(draft_dir))
        # 过滤出post目录中还没有content.md的
        folders = []
        for f in all_folders:
            post_content = os.path.join(agent_path, "post", f, "content.md")
            if not os.path.exists(post_content) or len(open(post_content).read()) < 5000:
                folders.append(f)
        
        if args.count:
            folders = folders[:args.count]
        elif not args.all:
            print(f"❌ 请指定 --count N 或 --all 或 --folder XXX")
            sys.exit(1)
    
    model = args.model
    print(f"🚀 盐选小说仿写 - {args.agent} (模型: {model})")
    print(f"   待处理: {len(folders)} 篇")
    if args.dry_run:
        print(f"   [DRY RUN]")
    
    success = 0
    fail = 0
    for folder in folders:
        try:
            if rewrite_folder(agent_path, folder, model=model, dry_run=args.dry_run):
                success += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            fail += 1
    
    print(f"\n{'='*60}")
    print(f"🏁 完成！成功 {success}，失败 {fail}")


if __name__ == "__main__":
    main()
