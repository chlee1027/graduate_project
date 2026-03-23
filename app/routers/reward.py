from fastapi import APIRouter, HTTPException
from app.schemas.request_response import RewardRequest, RewardResponse
from app.services.reward_service import calculate_reward
from app.services.recommender_bandit import update_bandit
from app.services.fake_db import logs_db

router = APIRouter()


@router.post("/", response_model=RewardResponse)
def reward(request: RewardRequest):
    reward_value, detail = calculate_reward(
        completed=request.completed,
        rpe=request.rpe,
        pain_occurred=request.pain_occurred,
        streak=request.streak
    )

    # 가장 최근 로그 중 같은 user의 plan_id를 찾아서 업데이트
    user_logs = [log for log in logs_db if log["user_id"] == request.user_id]
    if not user_logs:
        raise HTTPException(status_code=404, detail="No logs found for user")

    latest_log = user_logs[-1]
    plan_id = latest_log["plan_id"]

    update_bandit(plan_id, reward_value)

    return RewardResponse(
        reward=reward_value,
        detail=detail
    )