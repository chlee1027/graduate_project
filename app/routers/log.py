import json

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Recommendation, ExerciseLog, User
from app.schemas.request_response import LogRequest
from app.services.progression_service import check_user_progression
from app.services.plan_registry import ensure_plan_exists
from app.core.list_field import dump_list_field, parse_list_field
from app.services.auth import ensure_self, require_user

router = APIRouter()


@router.post("/")
def save_log(request: LogRequest, db: Session = Depends(get_db), auth_user: str = Depends(require_user)):
    ensure_self(auth_user, request.user_id)
    recommendation = (
        db.query(Recommendation)
        .filter(Recommendation.recommendation_id == request.recommendation_id)
        .first()
    )
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    ensure_self(auth_user, recommendation.user_id)

    # 대체 운동처럼 seed 에 없는 plan 이 추천될 수 있다. 그대로 넣으면
    # ExerciseLog.plan_id 외래키가 걸려 저장이 통째로 깨진다.
    selected_plan = json.loads(recommendation.selected_plan_json or "{}")
    if selected_plan.get("plan_id") == request.plan_id:
        ensure_plan_exists(db, selected_plan)

    pain_parts_str = ",".join(request.pain_parts) if request.pain_parts else None

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
        pain_parts=pain_parts_str,
        pain_severity=request.pain_severity,
        user_feedback=request.user_feedback,
    )

    db.add(log_item)

    # If severe pain, add to user injuries permanently
    if request.pain_occurred and request.pain_severity == "severe" and request.pain_parts:
        user = db.query(User).filter(User.user_id == request.user_id).first()
        if user:
            existing_injuries = parse_list_field(user.injuries)
            user.injuries = dump_list_field(existing_injuries + list(request.pain_parts))

    db.commit()
    db.refresh(log_item)

    # Check for level progression after saving log
    progression_result = check_user_progression(db, request.user_id)

    return {
        "message": "운동 로그가 저장되었습니다.",
        "progression": progression_result,
        "saved_log": {
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
            "pain_parts": log_item.pain_parts,
            "pain_severity": log_item.pain_severity,
            "user_feedback": log_item.user_feedback,
        },
    }
