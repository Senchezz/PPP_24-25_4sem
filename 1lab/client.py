import socket
import json
import os
import logging

class AudioClient:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        
        # Создаем папку для логирования, если её нет
        os.makedirs('./logs', exist_ok=True)

        # Настройка логирования
        logging.basicConfig(
            filename='logs/client.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            datefmt='%d.%m.%Y %H:%M:%S'
        )

        # Папка для сохранения сегментов аудио
        self.download_dir = './downloaded'
        os.makedirs(self.download_dir, exist_ok=True)

    def get_file_list(self):
        """Запрашивает у сервера список аудиофайлов."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(b'list')
            data = s.recv(4096)
            return json.loads(data.decode())

    def request_segment(self, filename, start, end):
        """Запрашивает отрезок аудио и сохраняет его локально."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(f'segment {filename} {start} {end}'.encode())
            
            # Сохраняем полученный отрезок
            save_path = os.path.join(
                self.download_dir,
                f'segment_{filename}_{start}_{end}.mp3'
            )
            with open(save_path, 'wb') as f:
                f.write(s.recv(4096))
            logging.info(f"Отрезок сохранен как {save_path}")

    def run(self):
        """Интерактивный режим работы клиента."""
        print("Аудио-клиент запущен. Доступные команды:")
        while True:
            print("\n1. Получить список файлов")
            print("2. Запросить отрезок аудио")
            print("3. Выход")
            choice = input("> ").strip()
            
            if choice == '1':
                logging.info(f"Отправлен запрос на получение списка аудиофайлов")
                files = self.get_file_list()
                logging.info(f"Получен список аудиофайлов")
                print("\nСписок аудиофайлов на сервере:")
                for idx, file in enumerate(files, 1):
                    print(f"{idx}. {file['name']} ({file['duration']:.2f} сек, {file['format']})")
            
            elif choice == '2':
                filename = input("Имя файла: ").strip()
                start = input("Начало отрезка (сек): ").strip()
                end = input("Конец отрезка (сек): ").strip()
                try:
                    self.request_segment(filename, float(start), float(end))
                    print("Отрезок успешно сохранен!")
                except ValueError:
                    print("Ошибка: введите числовые значения для времени!")
                except Exception as e:
                    print(f"Ошибка: {e}")
            
            elif choice == '3':
                break


if __name__ == '__main__':
    client = AudioClient()
    client.run()