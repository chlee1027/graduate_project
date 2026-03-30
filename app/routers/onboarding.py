import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.request_response import OnboardingRequest, OnboardingResponse

router = APIRouter()


@router.post("/", response_model=OnboardingResponse)
def onboarding(request: OnboardingRequest, db: Session = Depends(get_db)):
    initial_plan = {
        "recommended_days_per_week": min(request.weekly_available_days, 3),
        "recommended_minutes": 10 if request.experience_level == "beginner" else 20,
        "note": "초기에는 안전한 저강도 루틴부터 시작합니다.",
    }

    existing_user = db.query(User).filter(User.user_id == request.user_id).first()

    if existing_user:
        existing_user.age = request.age
        existing_user.sex = request.sex
        existing_user.height_cm = request.height_cm
        existing_user.weight_kg = request.weight_kg
        existing_user.goal = request.goal
        existing_user.experience_level = request.experience_level
        existing_user.injuries = json.dumps(request.injuries, ensure_ascii=False)
        existing_user.weekly_available_days = request.weekly_available_days
        existing_user.place_preference = request.place_preference
        existing_user.equipment = json.dumps(request.equipment, ensure_ascii=False)
    else:
        user = User(
            user_id=request.user_id,
            age=request.age,
            sex=request.sex,
            height_cm=request.height_cm,
            weight_kg=request.weight_kg,
            goal=request.goal,
            experience_level=request.experience_level,
            injuries=json.dumps(request.injuries, ensure_ascii=False),
            weekly_available_days=request.weekly_available_days,
            place_preference=request.place_preference,
            equipment=json.dumps(request.equipment, ensure_ascii=False),
        )
        db.add(user)

    db.commit()

    return OnboardingResponse(
        user_id=request.user_id,
        message="온보딩이 완료되었습니다.",
        initial_plan=initial_plan,
    )