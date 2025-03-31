import os
import json
import socket
import threading
import tempfile
import logging
from pydub import AudioSegment

class AudioServer:
    def __init__(self, host='127.0.0.1', port=65432, audio_dir='./audio_files'):
        self.host = host
        self.port = port
        self.audio_dir = audio_dir
        self.metadata_file = 'audio_metadata.json'
        
        # Создаем папку для логирования, если её нет
        os.makedirs('./logs', exist_ok=True)

        # Настройка логирования
        logging.basicConfig(
            filename='logs/server.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            datefmt='%d.%m.%Y %H:%M:%S'
        )

        # Создаем папку для аудио, если её нет
        os.makedirs(self.audio_dir, exist_ok=True)
        self.update_metadata()  # Обновляем метаданные при запуске

    def update_metadata(self):
        """Сканирует папку с аудио и сохраняет метаданные в формат JSON."""
        metadata = []
        for file in os.listdir(self.audio_dir):
            if file.endswith(('.mp3', '.wav', '.ogg')):  # Поддерживаемые форматы, можно и другие
                try:
                    audio = AudioSegment.from_file(os.path.join(self.audio_dir, file))
                    metadata.append({
                        'name': file,
                        'duration': len(audio) / 1000,  # Длительность в секундах
                        'format': os.path.splitext(file)[1].lower()  # Формат
                    })
                except Exception as e:
                    logging.error(f"Ошибка обработки файла {file}: {e}")
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        logging.info("Метаданные обновлены")

    def send_audio_segment(self, conn, filename, start_sec, end_sec):
        """Вырезает отрезок аудио и отправляет его клиенту."""
        try:
            if not os.path.exists(os.path.join(self.audio_dir, filename)):
                conn.sendall(b'File not found')
                return
            
            audio = AudioSegment.from_file(os.path.join(self.audio_dir, filename))
            start_ms = int(start_sec * 1000)  # Переводим в миллисекунды
            end_ms = int(end_sec * 1000)
            segment = audio[start_ms:end_ms]

            if start_ms < 0 or end_ms > len(audio) or start_ms >= end_ms:
                conn.sendall(b'Invalid time range')
                return
            
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                segment.export(tmp.name, format='mp3')

                with open(tmp.name, "rb") as f:
                    while chunk := f.read(4096):  # Отправка частями по 4 KB
                        conn.sendall(chunk)

            os.unlink(tmp.name)  # Удаляем временный файл

        except ValueError:
            conn.sendall(b'Invalid time values')
        except Exception as e:
            conn.sendall(f'Error: {str(e)}'.encode())

    def handle_client(self, conn, addr):
        """Обрабатывает подключение клиента."""
        logging.info(f"Подключен клиент: {addr}")
        try:
            data = conn.recv(4096).decode().strip()
            if not data:
                return

            if data == 'list':
                # Отправляем список аудиофайлов
                with open(self.metadata_file, 'rb') as f:
                    conn.sendall(f.read())
                logging.info(f"Клиенту {addr} отправлен список файлов")

            elif data.startswith('segment'):
                # Обработка запроса на вырезку отрезка
                _, filename, start, end = data.split('<sep>')
                self.send_audio_segment(conn, filename, float(start), float(end))
                logging.info(f"Клиенту {addr} отправлен отрезок из {filename}")

        except Exception as e:
            logging.error(f"Ошибка с клиентом {addr}: {e}")
        finally:
            conn.close()

    def run(self):
        """Запускает сервер."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            logging.info(f"Сервер запущен на {self.host}:{self.port}")
            print(f"Сервер слушает на {self.host}:{self.port}...")
            
            while True:
                conn, addr = s.accept()
                # Каждого клиента обрабатываем в отдельном потоке
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()


if __name__ == '__main__':
    server = AudioServer()
    server.run()