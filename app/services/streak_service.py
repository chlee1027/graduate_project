from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.timezone import kst_date, today_kst
from app.db.models import ExerciseLog


def get_current_streak(db: Session, user_id: str) -> int:
    """
    사용자의 현재 연속 운동일수(Streak)를 계산합니다.
    기록은 UTC 로 저장되므로 한국 날짜로 바꾼 뒤에 셉니다.
    """
    date_expr = kst_date(ExerciseLog.created_at)

    logs = (
        db.query(date_expr.label("workout_date"))
        .filter(ExerciseLog.user_id == user_id, ExerciseLog.completed == True)
        .group_by(date_expr)
        .order_by(date_expr.desc())
        .all()
    )

    if not logs:
        return 0

    workout_dates = {log.workout_date for log in logs}

    # 서버가 UTC 로 돌아도 같은 값이 나오도록 한국 날짜를 명시적으로 구한다.
    today = today_kst()
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
