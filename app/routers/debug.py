from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ExerciseLog, Recommendation, User
from uuid import uuid4

router = APIRouter()

from app.services.streak_service import get_current_streak

@router.post("/mock-yesterday/{user_id}")
def mock_yesterday_workout(user_id: str, db: Session = Depends(get_db)):
    """
    [DEBUG ONLY] 클릭할 때마다 스트릭을 1일씩 늘려줍니다.
    """
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        # 현재 스트릭 확인
        current_streak = get_current_streak(db, user_id)
        
        # 스트릭을 1일 더 늘리기 위해 과거의 날짜 계산
        # 만약 스트릭이 0이면 오늘(0일 전) 데이터를 생성
        # 만약 스트릭이 3이면 (0,1,2일 전 기록이 있는 상태), 3일 전 데이터를 생성
        target_time = datetime.now() - timedelta(days=current_streak)
        
        # 추천 생성
        rec_id = str(uuid4())
        mock_rec = Recommendation(
            recommendation_id=rec_id,
            user_id=user_id,
            state_json="{}",
            selected_plan_json=f'{{"plan_id": "debug_{current_streak}", "name": "스트릭 연장 테스트"}}',
            reason="debug",
            created_at=target_time
        )
        db.add(mock_rec)
        db.flush()
        
        # 로그 생성
        mock_log = ExerciseLog(
            recommendation_id=rec_id,
            user_id=user_id,
            plan_id=f"debug_{current_streak}",
            completed=True,
            actual_minutes=15,
            rpe=7.0,
            created_at=target_time
        )
        db.add(mock_log)
        
        db.commit()
        return {"message": f"Streak increased! New record added for {current_streak} days ago."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
