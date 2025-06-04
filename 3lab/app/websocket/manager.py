from typing import Dict
from fastapi import WebSocket
import json
import redis
import asyncio
from fastapi.encoders import jsonable_encoder

class ConnectionManager:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        
    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.redis.hset('websocket_connections', str(user_id), "connected")

    def disconnect(self, user_id: int):
        self.redis.hdel('websocket_connections', str(user_id))

    async def send(self, user_id: int, message: dict):
        print('SEND', user_id, self.redis)
        # Сохранить сообщение в Redis для последующей доставки
        message_queue = f"websocket:messages:{user_id}"
        self.redis.rpush(message_queue, json.dumps(jsonable_encoder(message)))
        self.redis.expire(message_queue, 60)

    async def listen_for_messages(self, user_id: int, websocket: WebSocket):
        pubsub = self.redis.pubsub()
        pubsub.subscribe(f"user:{user_id}")
        
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                try:
                    data = json.loads(message['data'])
                    await websocket.send_json(data)
                except Exception as e:
                    print(f"Ошибка обработки сообщения: {e}")
            await asyncio.sleep(0.1)

manager = ConnectionManager()