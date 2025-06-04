from pydantic import BaseModel, EmailStr
# EmailStr — специальный тип, который проверяет, что строка является корректным email-адресом

# Регистрация пользователя
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Вход пользователя
class UserOut(BaseModel):
    id: int
    email: EmailStr
    # from_attributes = True позволяет создавать объект UserOut напрямую из ORM-модели SQLAlchemy, без конвертации вручную
    class Config:
        from_attributes = True

# Публичный вывод пользователя
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Ответ с токеном
class TokenResponse(BaseModel):
    id: int
    email: EmailStr
    token: str
    class Config:
        from_attributes = True