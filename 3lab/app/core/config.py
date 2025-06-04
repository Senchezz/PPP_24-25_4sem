from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./app.db"  # Путь к SQLite базе
    JWT_SECRET_KEY: str = "fmeokOJ#Ijoj9J@ih*HnH*#h"   # Секретный ключ для JWT
    JWT_ALGORITHM: str = "HS256"              # Алгоритм для JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30     # Время жизни токена (30 минут)

    class Config:
        env_file = ".env"

settings = Settings()