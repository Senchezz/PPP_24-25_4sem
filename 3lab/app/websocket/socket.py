from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import jwt, JWTError
from app.websocket.manager import manager
from app.core.config import settings
from app.db.database import get_db
from app.models.user import User
import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    else:
        await websocket.close(code=1008)
        return

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_email = payload.get("sub")
        db = next(get_db())
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            await websocket.close(code=1008)
            return
        user_id = user.id
    except Exception as e:
        await websocket.close(code=1008)
        return

    await manager.connect(user_id, websocket)
    print(f"[WS] Подключен user_id={user_id}")

    try:
        message_queue = f"websocket:messages:{user_id}"
        while True:
            # Неблокирующая проверка очереди
            message_json = manager.redis.lpop(message_queue)
            if message_json:
                try:
                    await websocket.send_json(json.loads(message_json))
                except Exception as e:
                    print(f"Ошибка отправки сообщения: {e}")
                    break
            
            # Поддерживаем соединение
            try:
                # Проверяем, активно ли еще соединение
                await asyncio.wait_for(websocket.receive_text(), timeout=5)
            except asyncio.TimeoutError:
                # Таймаут - соединение активно, продолжаем
                continue
            except WebSocketDisconnect:
                # Соединение закрыто
                break
                
    except Exception as e:
        print(f"[WS] Ошибка: {e}")
    finally:
        manager.disconnect(user_id)
        print(f"[WS] Соединение закрыто user_id={user_id}")