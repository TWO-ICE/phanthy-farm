#!/usr/bin/env python3
"""
诊断 wemprss / phanthy 接口可达性。

用法:
  python3 diag.py
"""
import urllib.request, json, sys

def check(name, url, expected_in=None):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "diag/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode("utf-8", errors="ignore")[:500]
            ok = (expected_in in data) if expected_in else True
            print(f"  {'✅' if ok else '⚠️ '} {name}: HTTP {resp.status}")
            if not ok:
                print(f"     预期: 含 '{expected_in}'")
                print(f"     实际: {data[:200]}")
            return ok
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        return False

def main():
    print("=== wemprss ===")
    check("RSS feed", "https://wemprss.twoice.fun:666/rss/MP_WXS_3565048078?limit=1", "<rss")
    check("图片代理", "https://wemprss.twoice.fun:666/api/v1/wx/tools/image/proxy?url=https://mmbiz.qpic.cn/sz_mmbiz_jpg/E9h3abOJCem1vrBJHsnynkmSouuzFw5JzGEMa2I5vzNJlT3icicWyUmqxTp6q8rTSPT9w7NazTucg9DIIkzZgGP8ZS3zWeC452XY65kakQA3U/0?wx_fmt=jpeg")
    print()
    print("=== phanthy ===")
    check("skill.md", "https://phanthy.com/api/skill.md", "phanthy")
    check("heartbeat.md", "https://phanthy.com/api/heartbeat.md", "Heartbeat")

if __name__ == "__main__":
    main()
