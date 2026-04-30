from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.core.security import get_password_hash
from app.api.deps import get_current_user  # 추가

router = APIRouter()


@router.post("/signup", response_model=UserResponse)
async def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """회원 가입"""
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
async def read_user_me(current_user: User = Depends(get_current_user)):
    """현재 로그인한 사용자의 정보 반환"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """현재 로그인한 사용자의 정보 수정"""
    # 이메일 변경 시 중복 확인
    if user_in.email is not None and user_in.email != current_user.email:
        email_exists = db.query(User).filter(User.email == user_in.email).first()
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 이메일입니다.",
            )
        current_user.email = user_in.email

    # 전체 이름 변경
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name

    # 비밀번호 변경 (해싱 적용)
    if user_in.password is not None:
        current_user.hashed_password = get_password_hash(user_in.password)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user


@router.patch("/me", response_model=UserResponse)
async def patch_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """현재 로그인한 사용자의 정보 부분 수정 (PATCH)"""
    # 전송된 데이터만 추출 (unset된 필드 제외)
    update_data = user_in.model_dump(exclude_unset=True)

    if "email" in update_data:
        new_email = update_data["email"]
        if new_email != current_user.email:
            email_exists = db.query(User).filter(User.email == new_email).first()
            if email_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 사용 중인 이메일입니다.",
                )
            current_user.email = new_email

    if "full_name" in update_data:
        current_user.full_name = update_data["full_name"]

    if "password" in update_data:
        current_user.hashed_password = get_password_hash(update_data["password"])

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user
