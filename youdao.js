const crypto = require('crypto');

const BASE = 'https://dict-trans.youdao.com';
const PRODUCT = 'webfanyi';
const CLIENT = 'webmain';
const KEYFROM = 'webfanyi.webmain';
const GETTER_KEYID = 'translate-webmain-key-getter';
const TARGET_KEYID = 'translate-webfanyi-webmain';
const GETTER_SECRET = 'kSy5gtKA4yRUxAVPJPrdYKZ0jBKyd3t1';
const MODEL_NAME = 'llmLite';

const HEADERS = {
  'Accept': '*/*',
  'Origin': 'https://fanyi.youdao.com',
  'Referer': 'https://fanyi.youdao.com/',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
};

function md5hex(input) {
  return crypto.createHash('md5').update(String(input)).digest('hex');
}

function genSign(params, secret) {
  const p = { ...params };
  Object.keys(p).forEach((k) => { if (p[k] === '') delete p[k]; });
  const keys = Object.keys(p).sort().filter((k) => p[k] !== undefined);
  keys.push('key');
  p.key = secret;
  return [md5hex(keys.map((k) => `${k}=${p[k]}`).join('&')), keys.join(',')];
}

function genParamV3(e, t, n, r, o, i, a, s) {
  const l = {
    product: r, appVersion: a || 1, client: s || 'web', mid: 1, vendor: 'web', screen: 1,
    model: 1, imei: 1, network: 'wifi', keyfrom: o || 'fanyi.web', keyid: n,
    mysticTime: Date.now(), yduuid: i || 'abcdefg', abtest: 0, ...e
  };
  const [u, c] = genSign(l, t);
  Object.assign(l, { sign: u, pointParam: c });
  return l;
}

function newYduuid() {
  return crypto.randomBytes(16).toString('hex');
}

function toFormData(obj) {
  const fd = new FormData();
  Object.keys(obj).forEach((k) => {
    const v = obj[k];
    if (v !== '' && v !== null && v !== undefined) fd.append(k, v);
  });
  return fd;
}

function toUrlencoded(obj) {
  const uf = new URLSearchParams();
  Object.keys(obj).forEach((k) => {
    const v = obj[k];
    if (v !== '' && v !== null && v !== undefined) uf.append(k, v);
  });
  return uf;
}

async function getSecretKey(yduuid) {
  const params = genParamV3(
    { keyid: GETTER_KEYID, targetKeyid: TARGET_KEYID },
    GETTER_SECRET, GETTER_KEYID, PRODUCT, KEYFROM, yduuid, undefined, CLIENT
  );
  const r = await fetch(`${BASE}/translate/key`, {
    method: 'POST',
    headers: { ...HEADERS, 'Content-Type': 'application/x-www-form-urlencoded' },
    body: toUrlencoded(params)
  });
  const j = await r.json();
  if (j.code !== 0 || !j.data) throw new Error(`key-getter failed: ${JSON.stringify(j)}`);
  return j.data;
}

async function translate(text, from = 'en', to = 'zh-CHS', options = {}) {
  const yduuid = options.yduuid || newYduuid();
  const keys = options.keys || await getSecretKey(yduuid);

  const params = {
    product: PRODUCT, appVersion: 1, client: CLIENT, mid: 1, vendor: 'web', screen: 1,
    model: 1, imei: 1, network: 'wifi', keyfrom: KEYFROM, keyid: TARGET_KEYID,
    mysticTime: Date.now(), yduuid: yduuid, modelName: MODEL_NAME, useTerm: 'false',
    i: encodeURIComponent(text), from: from, to: to,
    signSecretKey: keys.secretKey, keyId: TARGET_KEYID, token: keys.token, source: CLIENT
  };
  const [sign, pointParam] = genSign(params, keys.secretKey);
  const body = { ...params, sign, pointParam };

  const r = await fetch(`${BASE}/webtranslate/sse`, {
    method: 'POST',
    headers: { ...HEADERS },
    body: toFormData(body)
  });
  if (r.status !== 200) throw new Error(`webtranslate/sse http ${r.status}`);

  const stream = await r.text();
  const chunks = [];
  for (const line of stream.split('\n')) {
    if (!line.startsWith('data:')) continue;
    try {
      const j = JSON.parse(line.slice(5).trim());
      if (j.transIncre) chunks.push(j.transIncre);
    } catch (e) {}
  }
  return { text: chunks.join(''), raw: stream, keys: keys };
}

module.exports = { genSign, genParamV3, getSecretKey, translate, md5hex, newYduuid, BASE };

if (require.main === module) {
  const input = process.argv[2] || 'Artificial intelligence is transforming the way we work and live.';
  const from = process.argv[3] || 'en';
  const to = process.argv[4] || 'zh-CHS';
  translate(input, from, to)
    .then((out) => console.log(out.text))
    .catch((e) => { console.error('FAILED:', e.message); process.exit(1); });
}
