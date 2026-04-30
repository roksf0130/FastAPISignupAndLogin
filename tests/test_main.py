import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.session import get_db, Base

# 테스트용 인메모리 SQLite DB 설정 (파일 생성 없이 메모리에서만 작동)
SQLALCHEMY_DATABASE_URL = "sqlite://"  # 또는 "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # 단일 커넥션을 공유하여 테이블 유지
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 테스트용 DB 의존성 주입
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    # 매 테스트마다 테이블 생성
    Base.metadata.create_all(bind=engine)
    yield
    # 매 테스트 종료 후 테이블 삭제
    Base.metadata.drop_all(bind=engine)


def test_signup_and_login():
    # 1. 회원가입 테스트
    signup_data = {
        "username": "testuser",
        "password": "testpassword",
        "email": "test@example.com",
        "full_name": "Test User",
    }
    response = client.post("/users/signup", json=signup_data)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

    # 2. 로그인 테스트 (Token 획득)
    login_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None

    # 3. 인증이 필요한 경로 접근 테스트
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

    # 4. 회원정보 변경 테스트
    update_data = {
        "password": "updatedpassword",
        "email": "updated@example.com",
        "full_name": "Updated User",
    }
    response = client.put("/users/me", headers=headers, json=update_data)
    assert response.status_code == 200
    updated_info = response.json()
    assert updated_info["email"] == "updated@example.com"
    assert updated_info["full_name"] == "Updated User"

    # 5. 변경된 비밀번호로 로그인
    new_login_data = {"username": "testuser", "password": "updatedpassword"}
    login_response = client.post("/auth/login", data=new_login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

    # 6.patch 메소드를 이용한 회원정보 변경 테스트
    update_data = {
        "password": "updatedpassword2",
        "email": "updated2@example.com",
        "full_name": "Updated2 User",
    }
    response = client.patch("/users/me", headers=headers, json=update_data)
    assert response.status_code == 200
    updated_info = response.json()
    assert updated_info["email"] == "updated2@example.com"
    assert updated_info["full_name"] == "Updated2 User"

    # 7. 변경된 비밀번호로 로그인
    new_login_data = {"username": "testuser", "password": "updatedpassword2"}
    login_response = client.post("/auth/login", data=new_login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_login_fail():
    # 존재하지 않는 사용자로 로그인 시도
    login_data = {"username": "nonexistent", "password": "wrongpassword"}
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 401
