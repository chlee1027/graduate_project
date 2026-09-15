from datetime import timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.timezone import now_kst
from app.db.database import get_db
from app.db.models import ExerciseLog, Recommendation, User
from app.services.plan_registry import ensure_plan_exists
from app.services.streak_service import get_current_streak

router = APIRouter()

# 이 기록이 가리킬 운동. seed 에 없는 id 라서 없으면 만들어 두고 쓴다.
# (없는 id 로 로그를 넣으면 ExerciseLog.plan_id 외래키에 걸려 저장이 깨진다)
DEBUG_PLAN = {
    "plan_id": "debug_streak_test",
    "name": "스트릭 연장 테스트",
    "location": "home",
    "type": "time-based",
    "target_parts": "full_body",
    "intensity": "low",
    "minutes": 15,
    "sets": 1,
    "reps": 1,
    "met_value": 3.0,
    # 근력 기록으로 둔다. 회복(스트레칭)으로 두면 주간 목표 달성도에 잡히지 않아
    # 스트릭만 늘고 화면의 다른 숫자는 그대로여서 헷갈린다.
    "is_stretching": False,
    "description": "스트릭 동작 확인용 기록입니다.",
}


@router.post("/mock-yesterday/{user_id}")
def mock_yesterday_workout(user_id: str, db: Session = Depends(get_db)):
    """
    [DEBUG ONLY] 클릭할 때마다 스트릭을 1일씩 늘려줍니다.
    """
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        ensure_plan_exists(db, DEBUG_PLAN)

        # 현재 스트릭 확인
        current_streak = get_current_streak(db, user_id)

        # 스트릭을 1일 더 늘리기 위해 과거의 날짜 계산
        # 만약 스트릭이 0이면 오늘(0일 전) 데이터를 생성
        # 만약 스트릭이 3이면 (0,1,2일 전 기록이 있는 상태), 3일 전 데이터를 생성
        # tz 정보가 붙은 한국 시각이라야 저장된 날짜가 의도한 날로 찍힌다.
        target_time = now_kst() - timedelta(days=current_streak)

        # 추천 생성
        rec_id = str(uuid4())
        mock_rec = Recommendation(
            recommendation_id=rec_id,
            user_id=user_id,
            state_json="{}",
            selected_plan_json=f'{{"plan_id": "{DEBUG_PLAN["plan_id"]}", "name": "{DEBUG_PLAN["name"]}"}}',
            reason="debug",
            created_at=target_time
        )
        db.add(mock_rec)
        db.flush()

        # 로그 생성
        mock_log = ExerciseLog(
            recommendation_id=rec_id,
            user_id=user_id,
            plan_id=DEBUG_PLAN["plan_id"],
            completed=True,
            actual_minutes=15,
            rpe=7.0,
            created_at=target_time
        )
        db.add(mock_log)

        db.commit()
        return {"message": f"Streak increased! New record added for {current_streak} days ago."}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
