from fastapi import APIRouter, HTTPException
from app.schemas.request_response import RecommendRequest, RecommendResponse
from app.services.fake_db import users_db, plans_db
from app.services.candidate_generator import generate_candidates
from app.services.recommender_bandit import select_action

router = APIRouter()


@router.post("/", response_model=RecommendResponse)
def recommend(request: RecommendRequest):
    user = users_db.get(request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please complete onboarding first.")

    state = request.model_dump()
    state["experience_level"] = user["experience_level"]

    candidates = generate_candidates(state)
    result = select_action(state, candidates)
    selected_plan = result["selected_plan"]

    plans_db[selected_plan["plan_id"]] = selected_plan

    return RecommendResponse(
        user_id=request.user_id,
        state=state,
        candidates=candidates,
        selected_plan=selected_plan,
        reason=result["reason"]
    )