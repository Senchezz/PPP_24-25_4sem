from fastapi import APIRouter, Depends
from app.schemas.encryption import *
from app.services import huffman, xor
from app.api.auth import get_current_user
from app.models.user import User
from app.celery.tasks import async_encode
import base64, uuid  # base64 для кодирования двоичных данных в строку и uuid для генерации уникальных ID

router = APIRouter()

# Синхронное кодирование текста
@router.post("/encode", response_model=EncodeResponse)
def encode_text(data: EncodeRequest):
    compressed, codes, padding = huffman.huffman_encode(data.text)
    encrypted = xor.xor_encrypt(compressed, data.key)
    b64 = base64.b64encode(encrypted).decode()
    return EncodeResponse(encoded_data=b64, key=data.key, huffman_codes=codes, padding=padding)

# Синхронное декодирование текста
@router.post("/decode", response_model=DecodeResponse)
def decode_text(data: DecodeRequest):
    raw = base64.b64decode(data.encoded_data)
    decrypted = xor.xor_decrypt(raw, data.key)
    text = huffman.huffman_decode(decrypted, data.huffman_codes, data.padding)
    return DecodeResponse(decoded_text=text)

# Асинхронное кодирование (через Celery)
@router.post("/encode/async")
def encode_async(data: EncodeRequest, user: User = Depends(get_current_user)):
    task_id = str(uuid.uuid4())
    async_encode.delay(user.id, data.text, data.key, task_id)
    return {"message": "Task started", "task_id": task_id}