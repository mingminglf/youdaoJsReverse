const crypto = require('crypto');

const SECRET_KEY = 'fsdsogkndfokasodnaso';
const SECRET_KEY_GETTER = 'asdjnjfenknafdfsdfsd';
const KEYID = 'webfanyi';
const KEYID_GETTER = 'webfanyi-key-getter';
const DECODE_KEY = 'ydsecret://query/key/B*RGygVywfNBwpmBaZg*WT7SIOUP2T0C9WHMZN39j^DAdaZhAnxvGcCY6VYFwnHl';
const DECODE_IV = 'ydsecret://query/iv/C@lZe2YzHtZ2CYgaXKSVfsb7Y4QWHjITPPZ0nQp87fBeJ!Iv6v^6fvi2WN@bYpJ4';

function md5Hex(input) {
  return crypto.createHash('md5').update(String(input)).digest('hex');
}

function md5Buf(input) {
  return crypto.createHash('md5').update(String(input)).digest();
}

function getSign(mysticTime, secretKey) {
  const t = mysticTime || Date.now();
  const k = secretKey || SECRET_KEY;
  return {
    sign: md5Hex(`client=fanyideskweb&mysticTime=${t}&product=webfanyi&key=${k}`),
    mysticTime: t
  };
}

function decodeData(data) {
  if (!data) return null;
  const normalized = data.replace(/-/g, '+').replace(/_/g, '/');
  const decipher = crypto.createDecipheriv('aes-128-cbc', md5Buf(DECODE_KEY), md5Buf(DECODE_IV));
  return decipher.update(Buffer.from(normalized, 'base64')).toString('utf8') + decipher.final('utf8');
}

module.exports = { getSign, decodeData, SECRET_KEY, DECODE_KEY, DECODE_IV };
