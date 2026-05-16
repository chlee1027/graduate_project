from sqlalchemy.orm import Session
from app.db.models import User, ExerciseLog


def check_user_progression(db: Session, user_id: str) -> dict:
    """
    사용자의 운동 기록을 분석하여 숙련도(experience_level)를 자동으로 승급시킵니다.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return {"upgraded": False}

    # 완료된 총 운동 횟수 조회
    completed_count = (
        db.query(ExerciseLog)
        .filter(ExerciseLog.user_id == user_id, ExerciseLog.completed == True)
        .count()
    )

    old_level = user.experience_level
    new_level = old_level

    # 승급 기준 설정
    # 초보 -> 중급: 15회 완료
    if old_level == "beginner" and completed_count >= 15:
        new_level = "intermediate"
    
    # 중급 -> 상급: 40회 완료
    elif old_level == "intermediate" and completed_count >= 40:
        new_level = "advanced"

    if new_level != old_level:
        user.experience_level = new_level
        db.commit()
        return {
            "upgraded": True,
            "old_level": old_level,
            "new_level": new_level,
            "total_completed": completed_count
        }

    return {
        "upgraded": False,
        "current_level": old_level,
        "total_completed": completed_count
    }
