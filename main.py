import requests
import execjs
import hashlib

from collections import OrderedDict
# 创建运行时环境
runtime = execjs.get()

# 读取 JavaScript 文件内容
with open('fy.js', 'r') as file:
    javascript_code = file.read()

# 编译 JavaScript 代码
ctx = runtime.compile(javascript_code)

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://fanyi.youdao.com",
    "Pragma": "no-cache",
    "Referer": "https://fanyi.youdao.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}
cookies = {
    "OUTFOX_SEARCH_USER_ID": "1634410890@10.112.57.88",
    "OUTFOX_SEARCH_USER_ID_NCOO": "559167954.0544283"
}
url = "https://dict.youdao.com/webtranslate"
data = {
    "i": "你好你好你好你好",
    "from": "zh-CHS",
    "to": "en",
    "domain": "0",
    "dictResult": "true",
    "keyid": "webfanyi",
    "sign": "cb9533c0fc351ce6b3b446b4ed331794",
    "client": "fanyideskweb",
    "product": "webfanyi",
    "appVersion": "1.0.0",
    "vendor": "web",
    "pointParam": "client,mysticTime,product",
    "mysticTime": "1695804852717",
    "keyfrom": "fanyi.web",
    "mid": "1",
    "screen": "1",
    "model": "1",
    "network": "wifi",
    "abtest": "0",
    "yduuid": "abcdefg"
}
while True:
    user_input = input("请输入内容：")  # 监听用户输入

    # 根据输入内容进行相应的处理和输出
    if user_input == "quit":




        print("程序已退出")
        break  # 如果输入为 "quit"，则退出循环
    else:
        # 调用 JavaScript 函数
        result = ctx.call('test')

        # 将字典转换为可修改的有序字典
        data_ordered = OrderedDict(data)

        # 计算新的 sign 值
        # new_sign = hashlib.md5("new_sign_value".encode()).hexdigest()

        # 更新 sign 值
        data_ordered["sign"] = result.get("sign")
        data_ordered["mysticTime"] = result.get("mysticTime")
        data_ordered["i"] = user_input
        # 将有序字典转换回普通的字典类型
        data = dict(data_ordered)

        response = requests.post(url, headers=headers, cookies=cookies, data=data)

        # print(response.text)
        # print(response)


        fanyiResult = ctx.call('results', response.text)
        print(fanyiResult)
        # print("您输入的内容是：", user_input)
