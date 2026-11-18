"""hybrid LinUCB 상태를 DB 에 두고 꺼내 쓰는 자리. 계산은 linucb.py."""

from __future__ import annotations

from datetime import timedelta
from typing import Dict, List, Optional

import numpy as np
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.timezone import now_kst
from app.db.models import ExerciseLog, LinUCBShared, LinUCBUser
from app.services import linucb as L

SHARED_ID = 1


def _arr(blob: bytes, shape) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float64).reshape(shape).copy()


def _blob(a: np.ndarray) -> bytes:
    return np.ascontiguousarray(a, dtype=np.float64).tobytes()


def load_shared(db: Session, for_update: bool = False) -> L.SharedState:
    q = db.query(LinUCBShared).filter(LinUCBShared.id == SHARED_ID)
    row = (q.with_for_update() if for_update else q).first()
    if row is None:
        return L.SharedState(lam=settings.LINUCB_LAMBDA)
    return L.SharedState(_arr(row.mat_a0, (L.D_SHARED, L.D_SHARED)), _arr(row.vec_b0, (L.D_SHARED,)))


def load_user(db: Session, user_id: str, for_update: bool = False) -> L.UserState:
    q = db.query(LinUCBUser).filter(LinUCBUser.user_id == user_id)
    row = (q.with_for_update() if for_update else q).first()
    if row is None:
        return L.UserState(lam=settings.LINUCB_LAMBDA)
    return L.UserState(_arr(row.mat_a, (L.D_USER, L.D_USER)), _arr(row.mat_b, (L.D_USER, L.D_SHARED)),
                       _arr(row.vec_b, (L.D_USER,)))


def _save(db: Session, user_id: str, shared: L.SharedState, user: L.UserState) -> None:
    srow = db.query(LinUCBShared).filter(LinUCBShared.id == SHARED_ID).first()
    if srow is None:
        srow = LinUCBShared(id=SHARED_ID, n_updates=0)
        db.add(srow)
    srow.mat_a0, srow.vec_b0 = _blob(shared.A0), _blob(shared.b0)
    srow.n_updates = (srow.n_updates or 0) + 1

    urow = db.query(LinUCBUser).filter(LinUCBUser.user_id == user_id).first()
    if urow is None:
        urow = LinUCBUser(user_id=user_id, n_updates=0)
        db.add(urow)
    urow.mat_a, urow.mat_b, urow.vec_b = _blob(user.A), _blob(user.B), _blob(user.b)
    urow.n_updates = (urow.n_updates or 0) + 1


def recent_plan_ids(db: Session, user_id: str, n: int = 2) -> List[str]:
    """최근 n 세션의 운동. 특징의 「최근 반복」 칸에 쓴다(시뮬레이터와 같이 완료 여부를 가리지 않는다)."""
    rows = (db.query(ExerciseLog.plan_id).filter(ExerciseLog.user_id == user_id)
            .order_by(ExerciseLog.created_at.desc(), ExerciseLog.log_id.desc()).limit(n).all())
    return [r.plan_id for r in rows]


def recent_activity(db: Session, user_id: str, weekly_available_days: int) -> Dict[str, float]:
    """최근 7일 순응도(완료 세션 수 / 주당 가능 일수, 1 이하)와 평균 RPE."""
    since = now_kst() - timedelta(days=7)
    rows = (db.query(ExerciseLog.completed, ExerciseLog.rpe)
            .filter(ExerciseLog.user_id == user_id, ExerciseLog.created_at >= since).all())
    done = sum(1 for r in rows if r.completed)
    rpes = [r.rpe for r in rows if r.rpe is not None]
    return {
        "recent_adherence_7d": min(1.0, done / max(1, weekly_available_days or 1)),
        "avg_rpe_last_7d": sum(rpes) / len(rpes) if rpes else 5.0,
    }


def select_hybrid_db(db: Session, user_id: str, state: Dict, candidates: List[Dict]) -> Dict:
    shared, user = load_shared(db), load_user(db, user_id)
    res = L.select(shared, user, state, candidates, state.get("recent_plan_ids", []),
                   settings.LINUCB_ALPHA, settings.BALANCE_WEIGHT)
    return {"selected_plan": candidates[res["index"]], "reason": "linucb", "linucb": res}


def update_hybrid_db(db: Session, user_id: str, state: Dict, selected_plan: Dict, reward: float) -> Optional[Dict]:
    """추천 때 저장한 state·운동으로 특징을 다시 만들어 보상을 반영한다. 커밋은 부른 쪽이 한다."""
    needed = ("experience_level", "fatigue", "available_minutes", "recent_adherence_7d")
    if any(state.get(k) is None for k in needed) or not selected_plan.get("target_parts"):
        return None   # 예전 형식의 추천 기록
    shared = load_shared(db, for_update=True)
    user = load_user(db, user_id, for_update=True)
    z, x = L.features_for(state, selected_plan, state.get("recent_plan_ids", []))
    L.observe(shared, user, z, x, reward)
    _save(db, user_id, shared, user)
    return {"updated": True}
