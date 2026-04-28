from pydantic import BaseModel, EmailStr, ConfigDict


# 로그인 요청 데이터
class UserLogin(BaseModel):
    username: str
    password: str


# 회원가입 요청 데이터
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


# 사용자 응답 데이터
class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    email: str | None = None
    is_active: bool

    # Pydantic 2.0 최신 설정 방식
    model_config = ConfigDict(from_attributes=True)


# 토큰 응답 데이터
class Token(BaseModel):
    access_token: str
    token_type: str
