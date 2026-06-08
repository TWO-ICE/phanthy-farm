# scripts/ — 龙虾农场配套脚本

每个脚本独立可调用，可被提示词中的 agent 直接 `python3 xxx.py` 使用。

## 脚本一览

| 脚本 | 用途 | 调用方 |
|---|---|---|
| `fetch_rss.py` | 从 wemprss 拉取博主 RSS，清洗成 Markdown | 阶段 0 |
| `score_images.py` | 正文配图打分 + 排除异常 + Top-3 选择 | 阶段 0 |
| `compose_cover.py` | PIL 图层合成（底图 + 标题字） | 阶段 3 |
| `upload_to_phanthy.py` | 走 `/file_share` 上传图片到 phanthy CDN | 阶段 3、4 |
| `audit_pending.py` | 素材包完整性硬审计 | 阶段 4 |
| `heartbeat.py` | 心跳主调度（多 agent 串行） | 阶段 4 |
| `daily_reset.py` | 跨日额度重置 + 健康自检 | cron 每日 |
| `diag.py` | 诊断工具：检查 wemprss / phanthy 接口可达性 | 故障排查 |

## 依赖

```bash
pip3 install feedparser Pillow imagehash requests
```

## 运行约定

- 所有脚本接受 `--agent-slug` 参数定位 workspace
- 全部支持 `--dry-run` 预览
- 错误退出码：0 OK / 1 业务错 / 2 网络错 / 3 协议错
