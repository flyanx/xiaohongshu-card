# 解密搜狐文章加密的图片 data-src (AES-ECB-PKCS7, key=www.sohu.com6666)
import base64, re, sys, io
from Crypto.Cipher import AES

KEY = b'www.sohu.com6666'

def decrypt(data):
    raw = base64.b64decode(data)
    aes = AES.new(KEY, AES.MODE_ECB)
    dec = aes.decrypt(raw)
    # 去掉 PKCS7 padding
    pad = dec[-1]
    if pad <= 16 and dec[-pad:] == bytes([pad]) * pad:
        dec = dec[:-pad]
    return dec.decode('utf-8', errors='ignore')

html = open(r'F:\WorkBuddy\2026-08-10-11-02-28\plasmid-card\article.html', encoding='utf-8', errors='ignore').read()

# 找所有 data-src（跳过已解密的真实 URL 和头像）
encrypted = []
for m in re.finditer(r'data-src="([^"]+)"', html):
    v = m.group(1)
    if v.startswith(('http', '//')) or '=' not in v:
        continue
    encrypted.append(v)

print(f'发现 {len(encrypted)} 个加密图片串\n')
for i, e in enumerate(encrypted):
    try:
        url = decrypt(e)
        print(f'[{i+1}] {url}')
    except Exception as ex:
        print(f'[{i+1}] 解密失败: {ex}')
