"""hybrid LinUCB 추천 (Li et al., "A Contextual-Bandit Approach to Personalized News Article
Recommendation", WWW 2010 의 Algorithm 2. 원 논문의 기사별 몫을 여기서는 사용자별로 둔다).

앱(recommend·reward 라우터)과 시뮬레이터(sim/policies.py)가 이 모듈 하나를 함께 쓴다.
DB 를 모르는 순수 계산만 둔다. 저장은 linucb_store.py.

점수 = z^T beta + x^T theta_u + alpha * sqrt(s) + balance_weight * (코치 점수 / 100)
  z: 공유 특징 (문맥 7 x 운동 15 = 105차원), 모든 사용자가 함께 배운다
  x: 사용자 특징 (강도 3 + 대분류 부위 8 = 11차원), 사용자마다 따로 배운다
  코치 점수: candidate_generator 의 priority_score (최근 7일 덜 한 부위일수록 크다)
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Sequence

import numpy as np

LEVELS = ["beginner", "intermediate", "advanced"]
INTENSITIES = ["low", "medium", "high"]
MAJOR_PARTS = ["legs", "chest", "back", "shoulder", "arms", "core", "cardio", "full_body"]

CTX_DIM = 7      # 1, 숙련도 셋, 피로도, 가용 시간, 최근 순응도
PLAN_DIM = 15    # 강도 셋, 대분류 부위 여덟, 스트레칭, 시간, 코치 점수, 최근 반복
D_SHARED = CTX_DIM * PLAN_DIM
D_USER = len(INTENSITIES) + len(MAJOR_PARTS)


def _split(s) -> List[str]:
    return [p.strip() for p in (s or "").split(",") if p.strip()]


def context_vec(state: Dict) -> np.ndarray:
    lvl = [1.0 if state["experience_level"] == l else 0.0 for l in LEVELS]
    return np.array([1.0, *lvl, state["fatigue"] / 5, state["available_minutes"] / 60,
                     state["recent_adherence_7d"]])


def plan_vec(c: Dict, recent_plan_ids: Sequence[str]) -> np.ndarray:
    inten = [1.0 if c["intensity"] == i else 0.0 for i in INTENSITIES]
    parts = set(_split(c["target_parts"]))
    major = [1.0 if p in parts else 0.0 for p in MAJOR_PARTS]
    repeat = sum(1 for pid in recent_plan_ids if pid == c["plan_id"]) / 2
    return np.array([*inten, *major, 1.0 if c.get("is_stretching") else 0.0, c["minutes"] / 30,
                     c.get("priority_score", 0) / 100, repeat])


def user_vec(c: Dict) -> np.ndarray:
    """사용자마다 따로 배우는 특징: 강도와 부위. 개인의 체력·선호를 잡으라고 둔다."""
    inten = [1.0 if c["intensity"] == i else 0.0 for i in INTENSITIES]
    parts = set(_split(c["target_parts"]))
    return np.array([*inten, *[1.0 if p in parts else 0.0 for p in MAJOR_PARTS]])


def shared_feats(state: Dict, cands: List[Dict], recent_plan_ids: Sequence[str]) -> np.ndarray:
    cx = context_vec(state)
    return np.stack([np.outer(cx, plan_vec(c, recent_plan_ids)).ravel() for c in cands])


def balance_term(cands: List[Dict]) -> np.ndarray:
    return np.array([c.get("priority_score", 0) / 100 for c in cands])


class SharedState:
    """모든 사용자가 함께 쓰는 몫. A0 는 (D_SHARED, D_SHARED), b0 는 (D_SHARED,)."""

    def __init__(self, A0: Optional[np.ndarray] = None, b0: Optional[np.ndarray] = None, lam: float = 1.0):
        self.A0 = np.eye(D_SHARED) * lam if A0 is None else A0
        self.b0 = np.zeros(D_SHARED) if b0 is None else b0


class UserState:
    """사용자 한 명의 몫. A 는 (D_USER, D_USER), B 는 (D_USER, D_SHARED), b 는 (D_USER,)."""

    def __init__(self, A=None, B=None, b=None, lam: float = 1.0):
        self.A = np.eye(D_USER) * lam if A is None else A
        self.B = np.zeros((D_USER, D_SHARED)) if B is None else B
        self.b = np.zeros(D_USER) if b is None else b


def scores(shared: SharedState, user: UserState, Z: np.ndarray, X: np.ndarray, A0_inv=None):
    """후보마다 (예측 평균, 분산 항 s). tests/test_sim.py 가 [z; x] 를 이은 능형 회귀와 맞춰 본다."""
    A0_inv = np.linalg.inv(shared.A0) if A0_inv is None else A0_inv
    Au_inv = np.linalg.inv(user.A)
    beta = A0_inv @ shared.b0
    theta = Au_inv @ (user.b - user.B @ beta)
    C = A0_inv @ user.B.T @ Au_inv
    Dm = Au_inv @ user.B @ A0_inv @ user.B.T @ Au_inv
    s = (np.einsum("ij,jk,ik->i", Z, A0_inv, Z)
         - 2 * np.einsum("ij,jk,ik->i", Z, C, X)
         + np.einsum("ij,jk,ik->i", X, Au_inv, X)
         + np.einsum("ij,jk,ik->i", X, Dm, X))
    return Z @ beta + X @ theta, s


def observe(shared: SharedState, user: UserState, z: np.ndarray, x: np.ndarray, reward: float) -> None:
    """보상 하나를 반영한다 (Algorithm 2 의 갱신 단계). shared 와 user 를 제자리에서 바꾼다."""
    Au_inv = np.linalg.inv(user.A)
    BtAi = user.B.T @ Au_inv
    shared.A0 += BtAi @ user.B
    shared.b0 += BtAi @ user.b
    user.A += np.outer(x, x)
    user.B += np.outer(x, z)
    user.b += reward * x
    Au_inv = np.linalg.inv(user.A)
    BtAi = user.B.T @ Au_inv
    shared.A0 += np.outer(z, z) - BtAi @ user.B
    shared.b0 += reward * z - BtAi @ user.b


def select(shared: SharedState, user: UserState, state: Dict, cands: List[Dict],
           recent_plan_ids: Sequence[str], alpha: float, balance_weight: float,
           rng: Optional[random.Random] = None, A0_inv=None) -> Dict:
    """후보 하나를 고른다. 동점은 무작위. 고른 번호와 점수 내역을 돌려준다."""
    Z = shared_feats(state, cands, recent_plan_ids)
    X = np.stack([user_vec(c) for c in cands])
    mean, s = scores(shared, user, Z, X, A0_inv)
    bonus = alpha * np.sqrt(np.maximum(s, 0))
    total = mean + bonus + balance_weight * balance_term(cands)
    best = np.flatnonzero(total >= total.max() - 1e-12)
    idx = int(best[(rng or random).randrange(len(best))])
    return {"index": idx, "mean": float(mean[idx]), "bonus": float(bonus[idx]), "score": float(total[idx])}


def features_for(state: Dict, cand: Dict, recent_plan_ids: Sequence[str]):
    """보상 때 갱신에 쓸 (z, x). 추천 때 저장해 둔 state·후보로 다시 만든다."""
    return shared_feats(state, [cand], recent_plan_ids)[0], user_vec(cand)
