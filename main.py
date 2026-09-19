import sys
import json
import time
import hashlib
import secrets
from urllib.parse import quote

import requests

BASE = "https://dict-trans.youdao.com"
PRODUCT = "webfanyi"
CLIENT = "webmain"
KEYFROM = "webfanyi.webmain"
GETTER_KEYID = "translate-webmain-key-getter"
TARGET_KEYID = "translate-webfanyi-webmain"
GETTER_SECRET = "kSy5gtKA4yRUxAVPJPrdYKZ0jBKyd3t1"
MODEL_NAME = "llmLite"

HEADERS = {
    "Accept": "*/*",
    "Origin": "https://fanyi.youdao.com",
    "Referer": "https://fanyi.youdao.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def md5_hex(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def gen_sign(params, secret):
    data = {k: v for k, v in params.items() if v != ""}
    keys = sorted(k for k in data if data[k] is not None)
    keys.append("key")
    data["key"] = secret
    sign_str = "&".join(f"{k}={data[k]}" for k in keys)
    return md5_hex(sign_str), ",".join(keys)


def gen_param_v3(extra, secret, keyid, product, keyfrom, yduuid=None, app_version=None, client=None):
    params = {
        "product": product,
        "appVersion": app_version or 1,
        "client": client or "web",
        "mid": 1,
        "vendor": "web",
        "screen": 1,
        "model": 1,
        "imei": 1,
        "network": "wifi",
        "keyfrom": keyfrom or "fanyi.web",
        "keyid": keyid,
        "mysticTime": int(time.time() * 1000),
        "yduuid": yduuid or "abcdefg",
        "abtest": 0,
    }
    params.update(extra)
    params["sign"], params["pointParam"] = gen_sign(params, secret)
    return params


def get_secret_key(yduuid):
    params = gen_param_v3(
        {"keyid": GETTER_KEYID, "targetKeyid": TARGET_KEYID},
        GETTER_SECRET, GETTER_KEYID, PRODUCT, KEYFROM, yduuid, None, CLIENT,
    )
    resp = requests.post(
        BASE + "/translate/key",
        data=params,
        headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    payload = resp.json()
    if payload.get("code") != 0 or not payload.get("data"):
        raise RuntimeError(f"key-getter failed: {payload}")
    return payload["data"]


def translate(text, from_lang="en", to_lang="zh-CHS", keys=None, yduuid=None):
    yduuid = yduuid or secrets.token_hex(16)
    keys = keys or get_secret_key(yduuid)
    params = {
        "product": PRODUCT,
        "appVersion": 1,
        "client": CLIENT,
        "mid": 1,
        "vendor": "web",
        "screen": 1,
        "model": 1,
        "imei": 1,
        "network": "wifi",
        "keyfrom": KEYFROM,
        "keyid": TARGET_KEYID,
        "mysticTime": int(time.time() * 1000),
        "yduuid": yduuid,
        "modelName": MODEL_NAME,
        "useTerm": "false",
        "i": quote(text, safe="!~*'()"),
        "from": from_lang,
        "to": to_lang,
        "signSecretKey": keys["secretKey"],
        "keyId": TARGET_KEYID,
        "token": keys["token"],
        "source": CLIENT,
    }
    params["sign"], params["pointParam"] = gen_sign(params, keys["secretKey"])
    files = {k: (None, str(v)) for k, v in params.items() if v not in (None, "")}
    resp = requests.post(
        BASE + "/webtranslate/sse",
        files=files,
        headers=HEADERS,
        stream=True,
        timeout=(10, 60),
    )
    if resp.status_code != 200:
        raise RuntimeError(f"webtranslate/sse http {resp.status_code}")
    chunks = []
    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data:"):
            continue
        try:
            payload = json.loads(line[5:].strip())
        except json.JSONDecodeError:
            continue
        if payload.get("transIncre"):
            chunks.append(payload["transIncre"])
    return "".join(chunks)


def pick_langs(text):
    if any("\u4e00" <= ch <= "\u9fff" for ch in text):
        return "zh-CHS", "en"
    return "en", "zh-CHS"


def main():
    args = sys.argv[1:]
    if args:
        text = args[0]
        from_lang = args[1] if len(args) > 1 else None
        to_lang = args[2] if len(args) > 2 else None
        if not from_lang or not to_lang:
            from_lang, to_lang = pick_langs(text)
        print(translate(text, from_lang, to_lang))
        return

    print("有道翻译（新版接口），输入 quit 退出")
    yduuid = secrets.token_hex(16)
    keys = None
    while True:
        try:
            text = input("请输入内容：")
        except (EOFError, KeyboardInterrupt):
            break
        if text.strip() in ("quit", "exit"):
            break
        if not text.strip():
            continue
        from_lang, to_lang = pick_langs(text)
        try:
            if keys is None:
                keys = get_secret_key(yduuid)
            print(translate(text, from_lang, to_lang, keys=keys, yduuid=yduuid))
        except Exception as exc:
            keys = None
            print(f"翻译失败：{exc}")


if __name__ == "__main__":
    main()
