import secrets

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.list_field import dump_list_field
from app.db.database import get_db
from app.db.models import Account, User
from app.schemas.request_response import OnboardingRequest, OnboardingResponse
from app.services.auth import create_session, hash_password, normalize_username, validate_credentials
from app.services.rate_limit import ip_limit

router = APIRouter()


@router.post("/", response_model=OnboardingResponse)
def onboarding(request: OnboardingRequest, http: Request, db: Session = Depends(get_db)):
    """가입. 기본 정보와 아이디·비밀번호를 받아 사용자와 계정을 만들고 로그인 토큰을 준다.
    정보 수정은 PUT /api/user/{user_id} 로 한다."""
    username = normalize_username(request.username)
    validate_credentials(username, request.password)
    if db.query(Account).filter(Account.username == username).first():
        raise HTTPException(status_code=409, detail="이미 쓰는 아이디예요.")
    ip_limit(db, http, "signup", settings.SIGNUPS_PER_IP_PER_HOUR, "가입 시도가 많아요. 잠시 뒤에 다시 해 주세요.")

    user_id = "u_" + secrets.token_hex(6)
    db.add(User(
        user_id=user_id,
        age=request.age,
        sex=request.sex,
        height_cm=request.height_cm,
        weight_kg=request.weight_kg,
        goal=request.goal,
        experience_level=request.experience_level,
        injuries=dump_list_field(request.injuries),
        weekly_available_days=request.weekly_available_days,
        place_preference=request.place_preference,
        equipment=dump_list_field(request.equipment),
    ))
    db.flush()
    db.add(Account(user_id=user_id, username=username, password_hash=hash_password(request.password)))
    db.commit()
    token = create_session(db, user_id)

    return OnboardingResponse(
        user_id=user_id,
        username=username,
        token=token,
        message="가입했어요.",
        initial_plan={
            "recommended_days_per_week": min(request.weekly_available_days, 3),
            "recommended_minutes": 10 if request.experience_level == "beginner" else 20,
            "note": "초기에는 안전한 저강도 루틴부터 시작합니다.",
        },
    )
