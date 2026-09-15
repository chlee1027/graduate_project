from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.list_field import parse_list_field
from app.db.database import get_db
from app.db.models import User
from app.services.streak_service import get_current_streak

from app.schemas.request_response import UserDetailResponse, UserUpdateRequest

router = APIRouter()


@router.get("/{user_id}/status")
def get_user_status(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_streak = get_current_streak(db, user_id)

    return {
        "user_id": user_id,
        "current_streak": current_streak,
        "goal": user.goal,
        "experience_level": user.experience_level,
    }


@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user_details(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserDetailResponse(
        user_id=user.user_id,
        age=user.age,
        sex=user.sex,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        goal=user.goal,
        experience_level=user.experience_level,
        injuries=parse_list_field(user.injuries),
        weekly_available_days=user.weekly_available_days,
        place_preference=user.place_preference,
        equipment=parse_list_field(user.equipment),
        created_at=user.created_at
    )


@router.put("/{user_id}")
def update_user_details(user_id: str, request: UserUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return {"message": "회원 정보가 성공적으로 수정되었습니다.", "user_id": user_id}
