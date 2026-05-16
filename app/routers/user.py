from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.services.streak_service import get_current_streak

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
