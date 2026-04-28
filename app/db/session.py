import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

# .env에서 데이터베이스 URL 가져오기
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# SQLite 는 check_same_thread=False 필수
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# DeclarativeBase 클래스를 상속받은 파이썬 클래스는
# "단순한 객체가 아닌 데이터베이스의 특정 테이블과 연결된 모델이다." 라는 것을 sqlalchemy 에세 알려줌
class Base(DeclarativeBase):
    pass


# DB 세션 의존성 주입을 위한 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
