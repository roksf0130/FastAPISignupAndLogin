from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import Token
from app.core.security import verify_password, create_access_token

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),  # JSON 대신 Form 데이터로 받음
):
    # 1. 사용자 조회 (form_data.username 사용)
    user = db.query(User).filter(User.username == form_data.username).first()

    # 2. 비밀번호 검증 (form_data.password 사용)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
        )

    # 3. 액세스 토큰 생성
    access_token = create_access_token(subject=user.username)

    # 4. 토큰 반환
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
