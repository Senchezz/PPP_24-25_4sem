from sqlalchemy import create_engine
# create_engine() — это функция из SQLAlchemy, которая создаёт объект подключения к базе данных (движок)
# Этот объект engine управляет пулом подключений и знает, как общаться с БД
# Он не открывает реальное соединение сразу, а делает это "по требованию" (lazy connection)

from sqlalchemy.orm import sessionmaker, declarative_base
# sessionmaker — фабрика для создания сессий, с помощью которых выполняются транзакции с БД
# declarative_base — функция, создающая базовый класс для моделей, от которого потом будут наследоваться все SQLAlchemy-модели

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
# connect_args={"check_same_thread": False} — параметр только для SQLite,
# он отключает проверку, что все подключения создаются в одном и том же потоке
# Это нужно, чтобы использовать SQLite в многопоточном приложении

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()  # Базовый класс для моделей

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()