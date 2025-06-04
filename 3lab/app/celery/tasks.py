from app.celery import celery_app
from app.websocket.manager import manager
from app.services import huffman, xor
from typing import Dict
import base64, asyncio


@celery_app.task
def async_encode(user_id: int, text: str, key: str, task_id: str):
    print(f"[TASK] Старт async_encode. user_id={user_id}, task_id={task_id}")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        print("[TASK] Шаг 1: отправка STARTED")
        loop.run_until_complete(manager.send(user_id, {
            "status": "STARTED", "task_id": task_id, "operation": "encode"
        }))

        print("[TASK] Шаг 2: кодирование Хаффмана")
        compressed, codes, padding = huffman.huffman_encode(text)

        print("[TASK] Шаг 3: отправка PROGRESS")
        loop.run_until_complete(manager.send(user_id, {
            "status": "PROGRESS", "task_id": task_id, "operation": "encode", "progress": 50
        }))

        print("[TASK] Шаг 4: XOR + base64")
        encrypted = xor.xor_encrypt(compressed, key)
        result = base64.b64encode(encrypted).decode()

        print("[TASK] Шаг 5: отправка COMPLETED")
        loop.run_until_complete(manager.send(user_id, {
            "status": "COMPLETED", "task_id": task_id, "operation": "encode",
            "result": {"encoded_data": result, "huffman_codes": codes, "padding": padding}
        }))

        print("[TASK] Задача успешно завершена")

    except Exception as e:
        print("[ERROR] Исключение в async_encode:", e)
        raise