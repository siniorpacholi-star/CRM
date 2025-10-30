from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # Обрезаем пароль до 72 байт если он слишком длинный
    if len(password.encode('utf-8')) > 72:
        logger.warning("Пароль слишком длинный, обрезаем до 72 байт")
        # Конвертируем в байты, обрезаем и обратно в строку
        password_bytes = password.encode('utf-8')[:72]
        # Пытаемся декодировать, игнорируя ошибки если обрезка пришлась на середину символа
        password = password_bytes.decode('utf-8', 'ignore')
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt