from fastapi import APIRouter, Depends, HTTPException  # HTTPException для генерации ошибок HTTP
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer  # схема безопасности для получения токена из заголовка Authorization: Bearer
from jose import jwt, JWTError
from app.schemas.user import *
from app.cruds import user as user_crud
from app.core.config import settings
from app.core.jwt import create_access_token
from app.db.database import SessionLocal
from app.models.user import User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Генератор, который создаёт сессию БД и гарантирует её закрытие после использования
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Получение текущего пользователя по токену
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = user_crud.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Регистрация пользователя
@router.post("/sign-up/", response_model=TokenResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="User already exists")
    created = user_crud.create_user(db, user.email, user.password)
    token = create_access_token({"sub": created.email})
    return TokenResponse(id=created.id, email=created.email, token=token)

# Проверка логина и пароля
@router.post("/login/", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, user.email)
    if not db_user or not user_crud.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.email})
    return TokenResponse(id=db_user.id, email=db_user.email, token=token)

# Получение текущего пользователя
@router.get("/users/me/", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user