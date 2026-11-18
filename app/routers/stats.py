from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.timezone import KST, kst_date, today_kst
from app.db.database import get_db
from app.db.models import ExerciseLog, ExercisePlan, User
from app.services.streak_service import get_current_streak

router = APIRouter()


def _workout_type(is_stretching: bool, location: str) -> str:
    """하루의 운동 성격을 한 낱말로 정한다. 홈 화면 주간 활동의 칸 색과 같은 값이다."""
    if is_stretching:
        return "stretch"
    return "gym" if location == "gym" else "home"


@router.get("/{user_id}/summary")
def get_user_stats_summary(user_id: str, db: Session = Depends(get_db)):
    """
    사용자의 전체 통계 및 주간 활동 현황을 가져옵니다.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. 전체 통계 계산 (기록된 로그와 플랜의 MET 값을 조인하여 칼로리 계산)
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

    # 2. 주간 활동 현황 (최근 7일, 한국 날짜 기준)
    today = today_kst()
    seven_days_ago = today - timedelta(days=6)

    date_expr = kst_date(ExerciseLog.created_at)
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

    # 하루에 여러 번 운동할 수 있으므로 날짜별로 먼저 모은다.
    # 근력 운동이 하나라도 있으면 그날은 운동한 날로 세고, 칸 색도 근력 쪽을 따른다.
    # (스트레칭을 먼저 했다는 이유로 그날 한 근력 운동이 빠지지 않게 한다)
    daily = {}
    weekly_calories = 0.0

    for log in weekly_logs:
        day = daily.setdefault(log.workout_date, {"has_workout": False, "has_gym": False})
        if not log.is_stretching:
            day["has_workout"] = True
            if log.location == "gym":
                day["has_gym"] = True

        weekly_calories += (log.met_value * 3.5 * user.weight_kg / 200 * log.actual_minutes)

    workout_map = {}
    for day_date, day in daily.items():
        if day["has_workout"]:
            workout_map[day_date] = "gym" if day["has_gym"] else "home"
        else:
            workout_map[day_date] = "stretch"

    completed_days_count = sum(1 for day in daily.values() if day["has_workout"])

    activity_chart = []
    for i in range(7):
        target_date = seven_days_ago + timedelta(days=i)
        activity_chart.append({
            "date": target_date.strftime("%Y-%m-%d"),
            "day_name": "월화수목금토일"[target_date.weekday()], 
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

    today = today_kst()
    seven_days_ago = today - timedelta(days=6)

    logs = (
        db.query(ExerciseLog, ExercisePlan)
        .join(ExercisePlan, ExerciseLog.plan_id == ExercisePlan.plan_id)
        .filter(
            ExerciseLog.user_id == user_id,
            ExerciseLog.completed == True,
            kst_date(ExerciseLog.created_at) >= seven_days_ago
        )
        .order_by(ExerciseLog.created_at.desc())
        .all()
    )

    result = []
    for log, plan in logs:
        calories = (plan.met_value * 3.5 * user.weight_kg / 200 * log.actual_minutes)
        # 화면에 보이는 날짜와 시각도 한국 시간으로 맞춘다.
        logged_at = log.created_at.astimezone(KST)
        result.append({
            "log_id": log.log_id,
            "plan_name": plan.name,
            "minutes": log.actual_minutes,
            "sets": log.actual_sets,
            "calories": round(calories, 1),
            "date": logged_at.strftime("%Y-%m-%d"),
            "time": logged_at.strftime("%H:%M"),
            "location": plan.location,
            "is_stretching": plan.is_stretching
        })

    return result
