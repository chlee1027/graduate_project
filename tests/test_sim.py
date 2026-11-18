"""시뮬레이터와 비교 방식의 계산 확인. DB 없이 돈다: python -m pytest tests"""
import math
import random

import numpy as np
import pytest

from app.services.candidate_generator import build_candidates
from app.services.reward_service import calculate_reward
from sim import simulator as S
from sim.policies import D_SHARED, D_USER, HybridLinUCB


def _user(cap=1.0, weak="knee"):
    return S.SimUser(user_id="t", experience_level="intermediate", capacity=cap,
                     pref={p: 0.3 for p in S.MAJOR_PARTS}, injuries=[], weak_joint=weak,
                     location="home", goal="health", weekly_days=4, arrival_day=0)


@pytest.mark.parametrize("plan_id,fatigue,cap", [
    ("home_squat_standard", 2, 1.0),   # 약한 관절(무릎)에 걸린다
    ("home_pushup_standard", 4, 0.2),  # 어렵다
    ("home_crunch", 0, 2.0),           # 쉽다
])
def test_expected_reward_matches_monte_carlo(plan_id, fatigue, cap):
    user = _user(cap)
    ctx = S.DayContext(fatigue=fatigue, minutes=30, want_stretching=False, session=True)
    cand = next(p for p in S.PLANS if p["plan_id"] == plan_id)
    op = S.outcome_params(user, ctx, cand)
    op["weak_joint"] = user.weak_joint
    exp = S.expected_reward(op, streak_if_done=3, streak_if_fail=2)
    rng = random.Random(0)
    n, tot = 200_000, 0.0
    for _ in range(n):
        out = S.draw_outcome(op, rng)
        tot += calculate_reward(out["completed"], out["rpe"], out["pain"], 3 if out["completed"] else 2)[0]
    # calculate_reward 는 소수 넷째 자리 반올림, 표준오차는 0.003 안팎
    assert abs(tot / n - exp) < 0.01


def test_hybrid_matches_joint_ridge():
    """두 사용자의 hybrid LinUCB 추정·분산이 [z; x_u1; x_u2] 를 이은 능형 회귀와 같은지."""
    rng = np.random.default_rng(0)
    pol = HybridLinUCB(seed=0, alpha=1.0)
    users = ["a", "b"]
    W, R = [], []
    for t in range(60):
        u = users[t % 2]
        z, x, r = rng.normal(size=D_SHARED) * 0.3, rng.normal(size=D_USER), rng.normal()
        pol.observe(u, z, x, r)
        w = np.zeros(D_SHARED + 2 * D_USER)
        w[:D_SHARED] = z
        off = D_SHARED + users.index(u) * D_USER
        w[off:off + D_USER] = x
        W.append(w); R.append(r)
    W, R = np.array(W), np.array(R)
    A = np.eye(W.shape[1]) + W.T @ W
    coef = np.linalg.solve(A, W.T @ R)
    Ai = np.linalg.inv(A)
    z, x = rng.normal(size=(3, D_SHARED)) * 0.3, rng.normal(size=(3, D_USER))
    mean, s = pol.scores("b", z, x)
    off = D_SHARED + D_USER
    w = np.hstack([z, np.zeros((3, D_USER)), x])
    np.testing.assert_allclose(mean, w @ coef, atol=1e-8)
    np.testing.assert_allclose(s, np.einsum("ij,jk,ik->i", w, Ai, w), atol=1e-8)


def _state(**kw):
    base = {"user_id": "t", "location": "home", "available_minutes": 30, "fatigue": 2,
            "pain_parts": [], "experience_level": "advanced", "goal": "health",
            "want_stretching": False, "equipment_available": [], "recent_adherence_7d": 1.0}
    base.update(kw)
    return base


def test_build_candidates_rules():
    usage = {"major": {}, "sub": {}}
    c = build_candidates(S.PLANS, _state(pain_parts=["knee"]), usage)
    assert c and all("knee" not in (p["avoid_if_pain"] or "") for p in c)
    c = build_candidates(S.PLANS, _state(fatigue=5), usage)
    assert c and all(p["is_stretching"] for p in c)
    c = build_candidates(S.PLANS, _state(experience_level="beginner"), usage)
    assert {p["intensity"] for p in c} == {"low"}
    c = build_candidates(S.PLANS, _state(available_minutes=5), usage)
    assert all(p["minutes"] <= 5 for p in c)
