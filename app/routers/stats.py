from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.db.database import get_db
from app.db.models import ExerciseLog, User
from app.services.streak_service import get_current_streak

router = APIRouter()

@router.get("/{user_id}/summary")
def get_user_stats_summary(user_id: str, db: Session = Depends(get_db)):
    """
    사용자의 전체 통계 및 주간 활동 현황을 가져옵니다.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. 전체 통계 계산
    total_stats = db.query(
        func.count(ExerciseLog.log_id).label("total_count"),
        func.sum(ExerciseLog.actual_minutes).label("total_minutes")
    ).filter(ExerciseLog.user_id == user_id, ExerciseLog.completed == True).first()

    # 2. 주간 활동 현황 (최근 7일)
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6)
    
    # KST 기준 날짜별 운동 정보 조회
    date_expr = func.date(func.timezone('Asia/Seoul', func.timezone('UTC', ExerciseLog.created_at)))
    # For simplicity, if multiple logs exist for one day, take the last one's location and stretch status
    weekly_logs = (
        db.query(
            date_expr.label("workout_date"),
            ExerciseLog.plan_id,
            ExerciseLog.user_id
        )
        .filter(
            ExerciseLog.user_id == user_id, 
            ExerciseLog.completed == True,
            date_expr >= seven_days_ago
        )
        .order_by(ExerciseLog.created_at.asc())
        .all()
    )

    # 응답 포맷 구성
    # Get all stretching plan IDs to identify them in logs
    from app.services.candidate_generator import EXERCISE_POOL
    stretching_ids = {ex["plan_id"] for ex in EXERCISE_POOL if ex.get("is_stretching")}
    gym_ids = {ex["plan_id"] for ex in EXERCISE_POOL if ex["location"] == "gym"}

    workout_map = {}
    for log in weekly_logs:
        w_type = "home"
        if log.plan_id in stretching_ids:
            w_type = "stretch"
        elif log.plan_id in gym_ids:
            w_type = "gym"
        workout_map[log.workout_date] = w_type

    activity_chart = []
    for i in range(7):
        target_date = seven_days_ago + timedelta(days=i)
        activity_chart.append({
            "date": target_date.strftime("%Y-%m-%d"),
            "day_name": target_date.strftime("%a"), 
            "completed": target_date in workout_map,
            "type": workout_map.get(target_date, "none")
        })

    return {
        "user_id": user_id,
        "total_completed_workouts": total_stats.total_count or 0,
        "total_workout_minutes": int(total_stats.total_minutes or 0),
        "current_streak": get_current_streak(db, user_id),
        "experience_level": user.experience_level,
        "activity_chart": activity_chart
    }
