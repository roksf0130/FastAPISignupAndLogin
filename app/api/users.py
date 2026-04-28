from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash
from app.api.deps import get_current_user  # 추가

router = APIRouter()


@router.post("/signup", response_model=UserResponse)
async def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    # ID 및 Email 중복 확인
    user_exists = (
        db.query(User)
        .filter((User.username == user_in.username) | (User.email == user_in.email))
        .first()
    )
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 사용자 또는 이메일입니다.",
        )

    # 사용자 객체 생성 (비밀번호 해싱 적용)
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
    )

    # DB 저장
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# 보호된 API (내 정보 보기)
@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)):
    """현재 로그인한 사용자의 정보를 반환합니다."""
    return current_user
