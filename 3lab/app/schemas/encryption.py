from pydantic import BaseModel
from typing import Dict

# Входной запрос на кодирование
class EncodeRequest(BaseModel):
    text: str
    key: str

# Ответ сервера после кодирования текста
class EncodeResponse(BaseModel):
    encoded_data: str
    key: str
    huffman_codes: Dict[str, str]
    padding: int

# Входной запрос на декодирование текста
class DecodeRequest(BaseModel):
    encoded_data: str
    key: str
    huffman_codes: Dict[str, str]
    padding: int

# Ответ сервера после декодирования текста
class DecodeResponse(BaseModel):
    decoded_text: str