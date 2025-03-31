import socket
import json
import os
import logging

class AudioClient:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        
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

            data = b""
            while True:
                chunk = s.recv(4096)  # Читаем частями по 4096 байт
                if not chunk:
                    break
                data += chunk

            return json.loads(data.decode())

    def request_segment(self, filename, start, end):
        """Запрашивает отрезок аудио и сохраняет его локально."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(f'segment<sep>{filename}<sep>{start}<sep>{end}'.encode())
            
            # Сохраняем путь к полученному отрезку
            save_path = os.path.join(
                self.download_dir,
                f"segment_{filename.split('.')[0].replace(' ', '_')}_{start}_{end}.mp3"
            )

            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk

            if data == b'File not found':
                print("Файл с таким именем не найден на сервере :(")
                logging.info(f"Пользователь запросил несуществующий файл - {save_path}")
            else:
                with open(save_path, 'wb') as f:
                        f.write(data)
                        print("Отрезок успешно сохранен!")
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
                except ValueError:
                    print("Ошибка: введите числовые значения для времени!")
                except Exception as e:
                    print(f"Ошибка: {e}")
            
            elif choice == '3':
                break


if __name__ == '__main__':
    client = AudioClient()
    client.run()