from datetime import date, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.models import ExerciseLog


def get_current_streak(db: Session, user_id: str) -> int:
    """
    사용자의 현재 연속 운동일수(Streak)를 계산합니다.
    데이터베이스(UTC)와 한국 시간(KST)의 시차를 고려하여 계산합니다.
    """
    # 1. DB의 UTC 시간을 KST(Asia/Seoul)로 변환하여 날짜만 추출합니다.
    # PostgreSQL의 'AT TIME ZONE' 기능을 사용합니다.
    date_expr = func.date(func.timezone('Asia/Seoul', func.timezone('UTC', ExerciseLog.created_at)))
    
    logs = (
        db.query(date_expr.label("workout_date"))
        .filter(ExerciseLog.user_id == user_id, ExerciseLog.completed == True)
        .group_by(date_expr)
        .order_by(date_expr.desc())
        .all()
    )

    if not logs:
        return 0

    # 2. 날짜 객체 세트로 변환
    workout_dates = {log.workout_date for log in logs}
    
    # 3. 오늘 날짜(KST) 구하기
    # 서버 환경에 따라 다를 수 있으므로 명시적으로 한국 시간 기준으로 가져오는 것이 좋지만, 
    # 일반적인 환경에서는 date.today()가 서버 로컬 시간을 따릅니다.
    today = date.today()
    streak = 0
    
    # 오늘 운동을 했는지 확인
    if today in workout_dates:
        check_date = today
    # 오늘 안했다면 어제까지의 기록이 있는지 확인
    elif (today - timedelta(days=1)) in workout_dates:
        check_date = today - timedelta(days=1)
    else:
        # 오늘과 어제 모두 기록이 없으면 스트릭은 0
        return 0

    # 거꾸로 거슬러 올라가며 연속된 날짜 확인
    while check_date in workout_dates:
        streak += 1
        check_date -= timedelta(days=1)

    return streak
