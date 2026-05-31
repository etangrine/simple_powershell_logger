import os
import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

PSK = "0feNcM1h9Cx2mWAopX6Rq8WZ9sHUvQG4TthfgCL2lk0="

def _get_key() -> bytes:
    return base64.b64decode(PSK)

def encrypt_payload(data: dict) -> str:

    plaintext = json.dumps(data).encode("utf-8")

    # PKCS7 padding
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()

    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(_get_key()), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    return base64.b64encode(iv + ciphertext).decode("ascii")
