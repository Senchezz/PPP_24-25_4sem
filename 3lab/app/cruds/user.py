from sqlalchemy.orm import Session
from app.models.user import User
from passlib.context import CryptContext

# Контекст шифрования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Находит пользователя в БД по email
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Создаёт нового пользователя в БД
def create_user(db: Session, email: str, password: str):
    hashed = pwd_context.hash(password)
    user = User(email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Проверяет, что введённый пароль plain соответствует хэшу hashed
def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)