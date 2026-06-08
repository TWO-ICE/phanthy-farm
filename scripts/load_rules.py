#!/usr/bin/env python3
"""
读 base + agent 的 AGENT_RULES.md, 合并覆盖, 返回结构化 dict。

支持两层 YAML front matter 解析, 不引外部依赖。

用法:
  python3 scripts/load_rules.py <agent_slug>
  python3 scripts/load_rules.py <agent_slug> --json
  python3 scripts/load_rules.py <agent_slug> --section image_pipeline
"""
import argparse, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_RULES = REPO_ROOT / "AGENT_RULES.md"


def parse_front_matter(md_path: Path) -> dict:
    """简单 YAML front matter 解析: 支持 2 层嵌套 + 列表。"""
    if not md_path.exists():
        return {}
    text = md_path.read_text()
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not m:
        return {}
    fm = m.group(1)
    result = {}
    current_section = None
    for line in fm.split('\n'):
        if not line.strip() or line.strip().startswith('#'):
            continue
        # 顶层 key: value 或 key: (开始 section)
        top_m = re.match(r'^(\w[\w_-]*):\s*(.*)', line)
        if top_m and not line.startswith(' '):
            key, val = top_m.group(1), top_m.group(2).strip()
            if val == '' or val == '|':
                current_section = key
                result[key] = {}
            else:
                result[key] = _parse_value(val)
                current_section = None
            continue
        # 嵌套 key: value
        sub_m = re.match(r'^\s+(\w[\w_-]*):\s*(.*)', line)
        if sub_m and current_section:
            skey, sval = sub_m.group(1), sub_m.group(2).strip()
            result[current_section][skey] = _parse_value(sval)
    return result


def _parse_value(val: str):
    """解析单个 YAML value: 支持 [list] / "string" / bare string。"""
    if val.startswith('[') and val.endswith(']'):
        items = [s.strip().strip('"\'') for s in val[1:-1].split(',') if s.strip()]
        return items
    if val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    if val.startswith("'") and val.endswith("'"):
        return val[1:-1]
    # 数字 / 布尔
    if val.lower() in ('true', 'false'):
        return val.lower() == 'true'
    try:
        return int(val)
    except ValueError:
        pass
    return val


def deep_merge(base: dict, override: dict) -> dict:
    """override 字段覆盖 base。嵌套 dict 逐层合并。"""
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser(description="加载并合并 AGENT_RULES.md (base + per-agent override)")
    ap.add_argument("agent_slug", help="agent slug, e.g. susu-fashion")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--section", help="只输出指定 section (e.g. image_pipeline)")
    args = ap.parse_args()

    base_fm = parse_front_matter(BASE_RULES)
    agent_md = REPO_ROOT / "agents" / args.agent_slug / "AGENT_RULES.md"
    agent_fm = parse_front_matter(agent_md)
    if not agent_fm:
        print(f"⚠️  {agent_md} 不存在或没有 front matter", file=sys.stderr)
        print(f"   → 仅使用 base 默认", file=sys.stderr)
    merged = deep_merge(base_fm, agent_fm)

    if args.section:
        if args.section in merged:
            merged = {args.section: merged[args.section]}
        else:
            print(f"❌ section '{args.section}' 不存在", file=sys.stderr)
            sys.exit(1)

    if args.json:
        import json
        print(json.dumps(merged, ensure_ascii=False, indent=2))
    else:
        print(f"=== 合并规则: {args.agent_slug} ===")
        for k, v in merged.items():
            print(f"\n  [{k}]")
            if isinstance(v, dict):
                for sk, sv in v.items():
                    sv_repr = repr(sv) if isinstance(sv, str) and len(sv) > 60 else sv
                    print(f"    {sk}: {sv_repr}")
            else:
                print(f"    = {v}")


if __name__ == "__main__":
    main()
