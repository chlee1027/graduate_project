"""온보딩 -> 추천 -> 로그 -> 보상 흐름을 SQLite 로 돌린다. PostgreSQL 없이 돈다: python -m pytest tests

스트릭 계산은 PostgreSQL 의 timezone() 을 쓰므로 0 으로 바꿔 끼운다. 그 밖의 경로는 앱 코드 그대로다.
"""
import json

import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.data.exercise_catalog import FINAL_EXERCISES
from app.db.database import Base, get_db
from app.db.models import ExercisePlan, LinUCBShared, LinUCBUser, Recommendation
from app.routers import log, onboarding, recommend, reward
from app.services import linucb as L
from app.services import linucb_store


@pytest.fixture()
def env(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as db:
        db.add_all(ExercisePlan(**ex) for ex in FINAL_EXERCISES)
        db.commit()

    app = FastAPI()
    app.include_router(onboarding.router, prefix="/api/onboarding")
    app.include_router(recommend.router, prefix="/api/recommend")
    app.include_router(log.router, prefix="/api/log")
    app.include_router(reward.router, prefix="/api/reward")

    def _db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _db
    monkeypatch.setattr(recommend, "get_current_streak", lambda db, uid: 0)
    monkeypatch.setattr(reward, "get_current_streak", lambda db, uid: 0)
    client = TestClient(app)
    r = client.post("/api/onboarding/", json={
        "user_id": "u1", "age": 25, "sex": "female", "height_cm": 165, "weight_kg": 55,
        "goal": "fitness", "experience_level": "intermediate", "injuries": ["knee"],
        "weekly_available_days": 4, "place_preference": "home", "equipment": []})
    assert r.status_code == 200
    return client, Session


def _session(client, fatigue=3, minutes=20):
    rec = client.post("/api/recommend/", json={
        "user_id": "u1", "location": "home", "available_minutes": minutes, "fatigue": fatigue})
    assert rec.status_code == 200, rec.text
    body = rec.json()
    plan = body["selected_plan"]
    lg = client.post("/api/log/", json={
        "recommendation_id": body["recommendation_id"], "user_id": "u1", "plan_id": plan["plan_id"],
        "completed": True, "actual_minutes": plan["minutes"], "rpe": 7})
    assert lg.status_code == 200, lg.text
    rw = client.post("/api/reward/", json={
        "recommendation_id": body["recommendation_id"], "user_id": "u1",
        "completed": True, "rpe": 7, "pain_occurred": False})
    assert rw.status_code == 200, rw.text
    return body, rw.json()


def test_flow_updates_hybrid_model(env, monkeypatch):
    monkeypatch.setattr(settings, "RECOMMENDER", "hybrid")
    client, Session = env
    body, rw = _session(client, fatigue=3, minutes=20)

    plan, state = body["selected_plan"], body["state"]
    assert plan["minutes"] <= 20
    assert "knee" not in (plan["avoid_if_pain"] or "")          # 신고한 부상이 걸러진다
    assert state["recent_adherence_7d"] is not None              # 서버가 채운다
    assert state["recent_plan_ids"] == []
    assert rw["detail"]["linucb"] == {"updated": True}

    # 저장된 모형 = 빈 모형에 같은 특징으로 observe 한 번
    shared, user = L.SharedState(), L.UserState()
    with Session() as db:
        rec = db.query(Recommendation).filter_by(recommendation_id=body["recommendation_id"]).one()
        st = json.loads(rec.state_json)
        z, x = L.features_for(st, json.loads(rec.selected_plan_json), st["recent_plan_ids"])
        L.observe(shared, user, z, x, rw["reward"])
        got_s = linucb_store.load_shared(db)
        got_u = linucb_store.load_user(db, "u1")
        np.testing.assert_allclose(got_s.A0, shared.A0)
        np.testing.assert_allclose(got_s.b0, shared.b0)
        np.testing.assert_allclose(got_u.B, user.B)
        assert db.query(LinUCBShared).one().n_updates == 1
        assert db.query(LinUCBUser).one().n_updates == 1

    # 다음 추천은 방금 한 운동을 「최근 반복」 칸에 넣는다
    body2, _ = _session(client, fatigue=1, minutes=45)
    assert body2["state"]["recent_plan_ids"] == [plan["plan_id"]]
    with Session() as db:
        assert db.query(LinUCBShared).one().n_updates == 2


def test_eps_greedy_still_selectable(env, monkeypatch):
    monkeypatch.setattr(settings, "RECOMMENDER", "eps_greedy")
    client, _ = env
    body, rw = _session(client)
    assert body["selected_plan"]["plan_id"]
    assert rw["detail"]["bandit_stat"]["count"] == 1
