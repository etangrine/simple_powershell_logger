import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

PSK = "0feNcM1h9Cx2mWAopX6Rq8WZ9sHUvQG4TthfgCL2lk0="

def _get_key() -> bytes:
    return base64.b64decode(PSK)

def decrypt_payload(encrypted_b64: str) -> dict:
    raw = base64.b64decode(encrypted_b64)
    iv = raw[:16]
    ciphertext = raw[16:]

    cipher = Cipher(algorithms.AES(_get_key()), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()

    return json.loads(plaintext.decode("utf-8"))