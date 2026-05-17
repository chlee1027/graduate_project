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

    # 1. 전체 통계 계산 (기록된 로그와 플랜의 MET 값을 조인하여 칼로리 계산)
    from app.db.models import ExercisePlan
    
    total_stats_query = (
        db.query(
            func.count(ExerciseLog.log_id).label("total_count"),
            func.sum(ExerciseLog.actual_minutes).label("total_minutes"),
            func.sum(ExercisePlan.met_value * 3.5 * user.weight_kg / 200 * ExerciseLog.actual_minutes).label("total_calories")
        )
        .join(ExercisePlan, ExerciseLog.plan_id == ExercisePlan.plan_id)
        .filter(ExerciseLog.user_id == user_id, ExerciseLog.completed == True)
        .first()
    )

    # 2. 주간 활동 현황 (최근 7일)
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6)
    
    # KST 기준 날짜별 운동 정보 조회
    date_expr = func.date(func.timezone('Asia/Seoul', func.timezone('UTC', ExerciseLog.created_at)))
    weekly_logs = (
        db.query(
            date_expr.label("workout_date"),
            ExerciseLog.plan_id,
            ExerciseLog.actual_minutes,
            ExercisePlan.met_value,
            ExercisePlan.is_stretching,
            ExercisePlan.location
        )
        .join(ExercisePlan, ExerciseLog.plan_id == ExercisePlan.plan_id)
        .filter(
            ExerciseLog.user_id == user_id, 
            ExerciseLog.completed == True,
            date_expr >= seven_days_ago
        )
        .order_by(ExerciseLog.created_at.asc())
        .all()
    )

    workout_map = {}
    completed_days_count = 0
    weekly_calories = 0.0

    for log in weekly_logs:
        # 일일 운동 타입 결정 (마지막 기록 기준)
        w_type = "home"
        if log.is_stretching:
            w_type = "stretch"
        elif log.location == "gym":
            w_type = "gym"
        
        if log.workout_date not in workout_map:
            if not log.is_stretching:
                completed_days_count += 1
            workout_map[log.workout_date] = w_type
        
        # 주간 누적 칼로리 계산
        weekly_calories += (log.met_value * 3.5 * user.weight_kg / 200 * log.actual_minutes)

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
        "total_completed_workouts": total_stats_query.total_count or 0,
        "total_workout_minutes": int(total_stats_query.total_minutes or 0),
        "total_calories": round(float(total_stats_query.total_calories or 0), 1),
        "weekly_calories": round(weekly_calories, 1),
        "current_streak": get_current_streak(db, user_id),
        "experience_level": user.experience_level,
        "weekly_goal": user.weekly_available_days,
        "completed_days_this_week": completed_days_count,
        "activity_chart": activity_chart
    }

@router.get("/{user_id}/weekly-details")
def get_weekly_workout_details(user_id: str, db: Session = Depends(get_db)):
    """
    이번 주 수행한 운동의 상세 목록을 가져옵니다.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6)
    
    from app.db.models import ExercisePlan
    logs = (
        db.query(ExerciseLog, ExercisePlan)
        .join(ExercisePlan, ExerciseLog.plan_id == ExercisePlan.plan_id)
        .filter(
            ExerciseLog.user_id == user_id,
            ExerciseLog.completed == True,
            func.date(func.timezone('Asia/Seoul', func.timezone('UTC', ExerciseLog.created_at))) >= seven_days_ago
        )
        .order_by(ExerciseLog.created_at.desc())
        .all()
    )

    result = []
    for log, plan in logs:
        calories = (plan.met_value * 3.5 * user.weight_kg / 200 * log.actual_minutes)
        result.append({
            "log_id": log.log_id,
            "plan_name": plan.name,
            "minutes": log.actual_minutes,
            "sets": log.actual_sets,
            "calories": round(calories, 1),
            "date": log.created_at.strftime("%Y-%m-%d"),
            "time": log.created_at.strftime("%H:%M"),
            "location": plan.location,
            "is_stretching": plan.is_stretching
        })

    return result
