import json
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User, Recommendation
from app.schemas.request_response import RecommendRequest, RecommendResponse
from app.services.candidate_generator import generate_candidates
from app.services.recommender_bandit_db import select_action_db
from app.services.streak_service import get_current_streak

router = APIRouter()


@router.post("/", response_model=RecommendResponse)
def recommend(request: RecommendRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found. Please complete onboarding first."
        )

    # Calculate current streak if not provided
    current_streak = request.streak
    if current_streak is None:
        current_streak = get_current_streak(db, request.user_id)

    state = request.model_dump()
    state["experience_level"] = user.experience_level
    state["streak"] = current_streak

    candidates = generate_candidates(state, db)
    result = select_action_db(db, request.user_id, state, candidates)
    selected_plan = result["selected_plan"]

    recommendation_id = str(uuid4())

    recommendation = Recommendation(
        recommendation_id=recommendation_id,
        user_id=request.user_id,
        state_json=json.dumps(state, ensure_ascii=False),
        selected_plan_json=json.dumps(selected_plan, ensure_ascii=False),
        reason=result["reason"],
    )

    db.add(recommendation)
    db.commit()

    return RecommendResponse(
        recommendation_id=recommendation_id,
        user_id=request.user_id,
        state=state,
        candidates=candidates,
        selected_plan=selected_plan,
        reason=result["reason"],
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
