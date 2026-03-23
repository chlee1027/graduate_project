from fastapi import APIRouter
from app.schemas.request_response import OnboardingRequest, OnboardingResponse
from app.services.fake_db import users_db

router = APIRouter()


@router.post("/", response_model=OnboardingResponse)
def onboarding(request: OnboardingRequest):
    initial_plan = {
        "recommended_days_per_week": min(request.weekly_available_days, 3),
        "recommended_minutes": 10 if request.experience_level == "beginner" else 20,
        "note": "초기에는 안전한 저강도 루틴부터 시작합니다."
    }

    users_db[request.user_id] = request.model_dump()

    return OnboardingResponse(
        user_id=request.user_id,
        message="온보딩이 완료되었습니다.",
        initial_plan=initial_plan
    )