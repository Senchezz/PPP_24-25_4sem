import asyncio
import websockets
import requests
import json

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

def try_login(email: str, password: str):
    response = requests.post(f"{BASE_URL}/login/", json={
        "email": email,
        "password": password
    })
    if response.status_code == 200:
        return response.json()["token"]
    return None

def register(email: str, password: str):
    response = requests.post(f"{BASE_URL}/sign-up/", json={
        "email": email,
        "password": password
    })
    if response.status_code == 200:
        print("Пользователь зарегистрирован.")
        return response.json()["token"]
    else:
        print("Ошибка регистрации:", response.text)
        exit(1)

def login_or_register(email: str, password: str):
    token = try_login(email, password)
    if token:
        print("Вход выполнен.")
        return token
    print("Пользователь не найден. Пытаемся зарегистрировать...")
    return register(email, password)

def start_encode(token: str, text: str, key: str):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/encode/async", json={
        "text": text,
        "key": key
    }, headers=headers)
    if response.status_code == 200:
        task_id = response.json()["task_id"]
        print(f"Задача отправлена. Task ID: {task_id}")
        return True
    else:
        print("Ошибка при отправке:", response.text)
        return False

async def listen_to_ws(token: str):
    headers = [("Authorization", f"Bearer {token}")]
    print("[DEBUG] Подключаемся к WebSocket с токеном:")
    print(token)
    print("[DEBUG] Заголовки:", headers)

    try:
        async with websockets.connect(WS_URL, extra_headers=headers) as websocket:
            print("Подключено к WebSocket. Ожидаем уведомления...")
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print("\nПолучено сообщение:", data)
                
                if data.get("status") == "COMPLETED":
                    print("\nРезультаты кодирования:")
                    print(f"Закодированные данные: {data['result']['encoded_data']}")
                    print(f"Коды Хаффмана: {data['result']['huffman_codes']}")
                    print(f"Дополнение: {data['result']['padding']}")
                    return True
    except Exception as e:
        print("[!] Ошибка WebSocket:", e)
        return False

async def main_loop(token: str):
    while True:
        print("\n" + "="*50)
        print("Ввод текста для шифрования (или 'exit' для выхода)")
        text = input("Текст: ")
        if text.lower() == 'exit':
            break
            
        key = input("Ключ XOR: ")
        
        if start_encode(token, text, key):
            await listen_to_ws(token)
        else:
            print("Не удалось отправить задачу на кодирование")

async def main():
    print("Вход в систему")
    email = input("Email: ")
    password = input("Пароль: ")

    token = login_or_register(email, password)
    await main_loop(token)

if __name__ == "__main__":
    asyncio.run(main())
