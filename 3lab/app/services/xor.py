def xor_encrypt(data: bytes, key: str) -> bytes:
    key_bytes = key.encode()
    return bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data))

def xor_decrypt(data: bytes, key: str) -> bytes:
    return xor_encrypt(data, key)  # симметричное