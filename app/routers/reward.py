import json

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Recommendation, ExerciseLog
from app.schemas.request_response import RewardRequest, RewardResponse
from app.services.reward_service import calculate_reward
from app.services.recommender_bandit_db import update_bandit_db
from app.services.streak_service import get_current_streak

router = APIRouter()


@router.post("/", response_model=RewardResponse)
def reward(request: RewardRequest, db: Session = Depends(get_db)):
    recommendation = (
        db.query(Recommendation)
        .filter(Recommendation.recommendation_id == request.recommendation_id)
        .first()
    )
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    matched_log = (
        db.query(ExerciseLog)
        .filter(
            ExerciseLog.recommendation_id == request.recommendation_id,
            ExerciseLog.user_id == request.user_id,
        )
        .order_by(ExerciseLog.log_id.desc())
        .first()
    )
    if not matched_log:
        raise HTTPException(status_code=404, detail="No log found for this recommendation_id")

    selected_plan = json.loads(recommendation.selected_plan_json)
    plan_id = selected_plan["plan_id"]

    # Calculate current streak if not provided
    current_streak = request.streak
    if current_streak is None:
        current_streak = get_current_streak(db, request.user_id)

    reward_value, detail = calculate_reward(
        completed=request.completed,
        rpe=request.rpe,
        pain_occurred=request.pain_occurred,
        streak=current_streak,
    )

    updated_stat = update_bandit_db(db, request.user_id, plan_id, reward_value)

    return RewardResponse(
        reward=reward_value,
        detail={
            **detail,
            "streak": current_streak,
            "recommendation_id": request.recommendation_id,
            "user_id": request.user_id,
            "plan_id": plan_id,
            "bandit_stat": updated_stat,
        },
    )