from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Recommendation, ExerciseLog
from app.schemas.request_response import LogRequest, LogResponse

router = APIRouter()


@router.post("/", response_model=LogResponse)
def save_log(request: LogRequest, db: Session = Depends(get_db)):
    recommendation = (
        db.query(Recommendation)
        .filter(Recommendation.recommendation_id == request.recommendation_id)
        .first()
    )
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    log_item = ExerciseLog(
        recommendation_id=request.recommendation_id,
        user_id=request.user_id,
        plan_id=request.plan_id,
        completed=request.completed,
        actual_minutes=request.actual_minutes,
        actual_sets=request.actual_sets,
        actual_reps=request.actual_reps,
        rpe=request.rpe,
        pain_occurred=request.pain_occurred,
        user_feedback=request.user_feedback,
    )

    db.add(log_item)
    db.commit()
    db.refresh(log_item)

    return LogResponse(
        message="운동 로그가 저장되었습니다.",
        saved_log={
            "log_id": log_item.log_id,
            "recommendation_id": log_item.recommendation_id,
            "user_id": log_item.user_id,
            "plan_id": log_item.plan_id,
            "completed": log_item.completed,
            "actual_minutes": log_item.actual_minutes,
            "actual_sets": log_item.actual_sets,
            "actual_reps": log_item.actual_reps,
            "rpe": log_item.rpe,
            "pain_occurred": log_item.pain_occurred,
            "user_feedback": log_item.user_feedback,
        },
    )