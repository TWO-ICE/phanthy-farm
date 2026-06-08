#!/usr/bin/env python3
"""
走 phanthy /file_share 流程上传图片到 CDN。

用法:
  python3 upload_to_phanthy.py --api-key phanthy_xxx --file path/to/01_cover.png
"""
import argparse, json, os, sys
from pathlib import Path
import urllib.request, urllib.parse

PHANTHY = "https://phanthy.com/api/v1"

def upload(api_key: str, file_path: Path) -> str:
    size = file_path.stat().st_size
    ext = file_path.suffix.lower().lstrip(".")
    ct_map = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
              "webp": "image/webp", "gif": "image/gif"}
    content_type = ct_map.get(ext)
    if not content_type:
        raise ValueError(f"不支持的格式: {ext}")

    # 1. 申请 uploadUrl
    req = urllib.request.Request(
        f"{PHANTHY}/openclaw/file_share",
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "filename": file_path.name,
            "contentType": content_type,
            "size": size,
        }).encode("utf-8"),
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    if not body.get("success"):
        raise RuntimeError(f"file_share 失败: {body}")
    data = body["data"]
    upload_url = data["uploadUrl"]
    public_url = data["publicUrl"]

    # 2. PUT 到 COS
    put_req = urllib.request.Request(
        upload_url, method="PUT",
        headers={"Content-Type": content_type},
        data=file_path.read_bytes(),
    )
    with urllib.request.urlopen(put_req, timeout=60) as resp:
        if resp.status not in (200, 204):
            raise RuntimeError(f"COS 上传失败: status={resp.status}")

    return public_url

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", required=True)
    ap.add_argument("--file", required=True)
    args = ap.parse_args()

    public_url = upload(args.api_key, Path(args.file))
    print(json.dumps({"file": args.file, "public_url": public_url}, ensure_ascii=False))

if __name__ == "__main__":
    main()
