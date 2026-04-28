import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt
from typing import Any, Union
import os
from dotenv import load_dotenv

load_dotenv()

# 환경 변수 설정
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


def get_password_hash(password: str) -> str:
    """비밀번호 해싱."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증."""
    try:
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)
    except Exception:
        return False


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """JWT 엑세스 토큰 생성."""
    # 토큰 만료 시간 설정. 만료시간을 매개변수로 받으면 넘겨 받은 값을 설정하고, 값을 받지 않으면 기본값으로 설정
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
