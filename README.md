# youdaoJsReverse

有道翻译网页版 API 逆向（2026 更新版）。

## 现状（2026-09）

有道已将网页版翻译迁移到新接口：

| | 旧版（2023） | 新版（当前） |
| --- | --- | --- |
| 接口域名 | `dict.youdao.com` | `dict-trans.youdao.com` |
| 密钥 | 固定 key `fsdsogkndfokasodnaso` | 先调 `/translate/key` 领取动态 `token` + `secretKey` |
| 签名 | `md5(client=...&mysticTime=...&product=...&key=...)` | 全部参数按 key 排序拼串后取 md5（见 `genSign`） |
| 返回 | AES 加密后 base64 | SSE 流式明文（`transIncre` 增量） |

**旧版方案已不可用**：服务端对旧签名仍返回 HTTP 200、`code: 0`，但翻译内容是随机假结果（投毒反爬）。旧代码仅作学习参考。

## 使用

### Python

```bash
pip install requests
python main.py "Hello world"                # 自动判断翻译方向
python main.py "Hello world" en zh-CHS      # 英 -> 中
python main.py                              # 交互模式，quit 退出
```

### Node.js（无需第三方依赖，Node 18+）

```bash
node youdao.js "今天天气很好" zh-CHS en
```

## 新版流程

1. 取密钥：`POST https://dict-trans.youdao.com/translate/key`（表单），参数含 `keyid=translate-webmain-key-getter`、`targetKeyid=translate-webfanyi-webmain`，用固定引导密钥 `kSy5gtKA4yRUxAVPJPrdYKZ0jBKyd3t1` 签名，返回 `{token, secretKey}`。
2. 签名规则：把全部参与参数（含 `modelName`、`useTerm`、`signSecretKey`、`token` 等）按 key 排序，拼成 `k=v&k=v...`，末尾追加 `&key=<secretKey>`，取 MD5 十六进制即 `sign`；参与签名的 key 列表即 `pointParam`。
3. 翻译：`POST https://dict-trans.youdao.com/webtranslate/sse`（multipart 表单），响应为 `text/event-stream`，`event: message` 中 `data.transIncre` 逐段拼接即为完整译文。

## 文件说明

- `main.py` — Python 客户端（新版流程，可直接使用）
- `youdao.js` — Node.js 客户端（新版流程，可直接使用）
- `youdao_crypto.js` — 从旧版 bundle 中剥离出的签名 / AES 解密算法（2023 方案，仅作参考）
- `fy.js` — 2023 年抓取的有道页面 webpack bundle（仅供学习，不再使用）

## 说明

本项目仅用于学习和研究网页协议，请遵守目标网站的服务条款并控制请求频率。
