# youdaoJsReverse

有道翻译网页版 API 逆向。

## 使用

### Python

```bash
pip install requests
python main.py "Hello world"                # 自动判断翻译方向
python main.py "Hello world" en zh-CHS      # 英 -> 中
python main.py                              # 交互模式，quit 退出
```

### Node.js（Node 18+，无需依赖）

```bash
node youdao.js "今天天气很好" zh-CHS en
```

## 文件

- `main.py` — Python 客户端
- `youdao.js` — Node.js 客户端
- `youdao_crypto.js` — 旧版签名 / AES 解密算法
- `fy.js` — 2023 年抓取的页面 bundle（仅作学习）
