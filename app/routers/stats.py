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
    # DB에서 스트레칭 및 헬스장 운동 ID 목록 가져오기
    from app.db.models import ExercisePlan
    all_plans = db.query(ExercisePlan.plan_id, ExercisePlan.location, ExercisePlan.is_stretching).all()
    stretching_ids = {p.plan_id for p in all_plans if p.is_stretching}
    gym_ids = {p.plan_id for p in all_plans if p.location == "gym"}

    workout_map = {}
    completed_days_count = 0
    for log in weekly_logs:
        w_type = "home"
        is_stretching = False
        if log.plan_id in stretching_ids:
            w_type = "stretch"
            is_stretching = True
        elif log.plan_id in gym_ids:
            w_type = "gym"
        
        if log.workout_date not in workout_map:
            if not is_stretching:
                completed_days_count += 1
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
        "weekly_goal": user.weekly_available_days,
        "completed_days_this_week": completed_days_count,
        "activity_chart": activity_chart
    }

@router.get("/{user_id}/weekly-details")
def get_weekly_workout_details(user_id: str, db: Session = Depends(get_db)):
    """
    이번 주 수행한 운동의 상세 목록을 가져옵니다.
    """
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6)
    
    from app.db.models import ExercisePlan
    # DB에서 플랜 정보 미리 로드
    plans = db.query(ExercisePlan).all()
    plan_map = {p.plan_id: p for p in plans}

    logs = (
        db.query(ExerciseLog)
        .filter(
            ExerciseLog.user_id == user_id,
            ExerciseLog.completed == True,
            func.date(func.timezone('Asia/Seoul', func.timezone('UTC', ExerciseLog.created_at))) >= seven_days_ago
        )
        .order_by(ExerciseLog.created_at.desc())
        .all()
    )

    result = []
    for log in logs:
        plan_info = plan_map.get(log.plan_id)
        result.append({
            "log_id": log.log_id,
            "plan_name": plan_info.name if plan_info else "Unknown Exercise",
            "minutes": log.actual_minutes,
            "sets": log.actual_sets,
            "date": log.created_at.strftime("%Y-%m-%d"),
            "time": log.created_at.strftime("%H:%M"),
            "location": plan_info.location if plan_info else "home",
            "is_stretching": plan_info.is_stretching if plan_info else False
        })

    return result
