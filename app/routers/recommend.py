import json
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User, Recommendation, ExerciseLog
from app.schemas.request_response import RecommendRequest, RecommendResponse
from app.services.candidate_generator import generate_candidates
from app.services.recommender_bandit_db import select_action_db
from app.services.streak_service import get_current_streak
from datetime import datetime, timedelta

router = APIRouter()


@router.post("/", response_model=RecommendResponse)
def recommend(request: RecommendRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found. Please complete onboarding first."
        )

    # 1. 영구 부상 리스트 (User model)
    injuries = set([p.strip() for p in (user.injuries or "").split(",") if p.strip()])

    # 2. 최근 7일간 보고된 통증 부위 (ExerciseLog) - Dynamic blacklisting
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_pain_logs = (
        db.query(ExerciseLog.pain_parts)
        .filter(
            ExerciseLog.user_id == request.user_id,
            ExerciseLog.pain_occurred == True,
            ExerciseLog.created_at >= seven_days_ago
        )
        .all()
    )
    
    recent_pain_parts = set()
    for log in recent_pain_logs:
        if log.pain_parts:
            parts = [p.strip() for p in log.pain_parts.split(",") if p.strip()]
            recent_pain_parts.update(parts)

    # 영구 부상과 최근 통증 합치기
    all_pain_parts = list(injuries.union(recent_pain_parts))

    # Calculate current streak if not provided
    current_streak = request.streak
    if current_streak is None:
        current_streak = get_current_streak(db, request.user_id)

    state = request.model_dump()
    state["experience_level"] = user.experience_level
    state["streak"] = current_streak
    state["pain_parts"] = all_pain_parts # 프런트에서 보낸 것 대신 서버에서 계산한 값 사용

    candidates = generate_candidates(state, db)
    result = select_action_db(db, request.user_id, state, candidates)
    selected_plan = result["selected_plan"]
    
    # PT 코치 사유를 최우선으로, 없으면 알고리즘 사유(exploration/exploitation) 사용
    final_reason = selected_plan.get("coach_reason") or result["reason"]

    recommendation_id = str(uuid4())

    recommendation = Recommendation(
        recommendation_id=recommendation_id,
        user_id=request.user_id,
        state_json=json.dumps(state, ensure_ascii=False),
        selected_plan_json=json.dumps(selected_plan, ensure_ascii=False),
        reason=final_reason,
    )

    db.add(recommendation)
    db.commit()

    return RecommendResponse(
        recommendation_id=recommendation_id,
        user_id=request.user_id,
        state=state,
        candidates=candidates,
        selected_plan=selected_plan,
        reason=final_reason,
    )


@router.get("/{recommendation_id}")
def get_recommendation(recommendation_id: str, db: Session = Depends(get_db)):
    recommendation = db.query(Recommendation).filter(Recommendation.recommendation_id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    return {
        "recommendation_id": recommendation.recommendation_id,
        "user_id": recommendation.user_id,
        "selected_plan": json.loads(recommendation.selected_plan_json),
        "created_at": recommendation.created_at
    }
