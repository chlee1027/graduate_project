import json
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User, Recommendation, ExerciseLog
from app.schemas.request_response import RecommendRequest, RecommendResponse
from app.services.candidate_generator import generate_candidates
from app.services.recommender_bandit_db import select_action_db
from app.services.linucb_store import recent_activity, recent_plan_ids, select_hybrid_db
from app.core.config import settings
from app.services.streak_service import get_current_streak
from app.core.list_field import parse_list_field
from app.core.timezone import now_kst
from datetime import timedelta
from app.services.auth import ensure_self, require_user

router = APIRouter()


@router.post("/", response_model=RecommendResponse)
def recommend(request: RecommendRequest, db: Session = Depends(get_db), auth_user: str = Depends(require_user)):
    ensure_self(auth_user, request.user_id)
    user = db.query(User).filter(User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found. Please complete onboarding first."
        )

    # 1. 영구 부상 리스트 (User model)
    injuries = set(parse_list_field(user.injuries))

    # 2. 최근 7일간 보고된 통증 부위 (ExerciseLog) - Dynamic blacklisting
    # tz 정보가 붙은 시각이라야 timestamptz 인 created_at 과 어긋나지 않는다.
    seven_days_ago = now_kst() - timedelta(days=7)
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
    state["goal"] = user.goal
    state["streak"] = current_streak
    state["pain_parts"] = all_pain_parts # 프런트에서 보낸 것 대신 서버에서 계산한 값 사용
    # 프런트가 비워 보내면 최근 7일 기록으로 채운다
    activity = recent_activity(db, request.user_id, user.weekly_available_days)
    for key, value in activity.items():
        if state.get(key) is None:
            state[key] = value
    # 보상 때 같은 특징을 다시 만들 수 있도록 state 에 함께 저장한다
    state["recent_plan_ids"] = recent_plan_ids(db, request.user_id)

    candidates = generate_candidates(state, db)
    if settings.RECOMMENDER == "hybrid":
        result = select_hybrid_db(db, request.user_id, state, candidates)
    else:
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
def get_recommendation(recommendation_id: str, db: Session = Depends(get_db), auth_user: str = Depends(require_user)):
    recommendation = db.query(Recommendation).filter(Recommendation.recommendation_id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    ensure_self(auth_user, recommendation.user_id)
    
    return {
        "recommendation_id": recommendation.recommendation_id,
        "user_id": recommendation.user_id,
        "selected_plan": json.loads(recommendation.selected_plan_json),
        "created_at": recommendation.created_at
    }
