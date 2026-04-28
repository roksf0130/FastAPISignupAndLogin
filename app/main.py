from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import login, users
from app.db.session import engine, Base
from app.models import user

# SQLite 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="My FastAPI Project")

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (개발 시에만 사용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(login.router, prefix="/auth", tags=["login"])
app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/")
def read_root():
    return {"Hello": "World"}
