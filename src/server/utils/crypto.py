import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# AES encryption requires a 32-byte key (256-bit)
AES_KEY = os.getenv("AES_SECRET_KEY")

if not AES_KEY:
    raise ValueError("AES_SECRET_KEY missing in .env")

# Convert key to bytes
key = AES_KEY.encode()
if len(key) != 32:
    raise ValueError("AES_SECRET_KEY must be exactly 32 characters long")


def encrypt_token(token: str) -> str:
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(token.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode()
    ct = base64.b64encode(ct_bytes).decode()
    return f"{iv}:{ct}"


def decrypt_token(token_enc: str) -> str:
    iv_str, ct_str = token_enc.split(":")
    iv = base64.b64decode(iv_str)
    ct = base64.b64decode(ct_str)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    token = unpad(cipher.decrypt(ct), AES.block_size).decode()
    return token
