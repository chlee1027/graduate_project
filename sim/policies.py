"""비교할 추천 방식들. 모두 select(user_id, state, candidates, hist) -> 고른 후보의 번호.

hist["true_expected"] 는 숨은 속성으로 계산한 기대 보상이다. Oracle 만 쓰고 나머지는 보지 않는다.
"""

from __future__ import annotations

import random
from typing import Dict, List

import numpy as np

from app.services.recommender_bandit_db import select_action

LEVELS = ["beginner", "intermediate", "advanced"]
INTENSITIES = ["low", "medium", "high"]
MAJOR_PARTS = ["legs", "chest", "back", "shoulder", "arms", "core", "cardio", "full_body"]


def _split(s):
    return [p.strip() for p in (s or "").split(",") if p.strip()]


class Policy:
    name = "base"

    def __init__(self, seed: int):
        self.rng = random.Random(f"policy|{self.name}|{seed}")

    def select(self, user_id: str, state: Dict, cands: List[Dict], hist: Dict) -> int:
        raise NotImplementedError

    def update(self, user_id, state, cands, idx, hist, reward):
        pass


class RandomPolicy(Policy):
    """후보 가운데 아무거나."""
    name = "random"

    def select(self, user_id, state, cands, hist):
        return self.rng.randrange(len(cands))


class RulePolicy(Policy):
    """앱의 손 규칙만(부위 우선순위 + 상황 가산점). 보상으로 배우지 않는다. 동점은 무작위."""
    name = "rule"

    def select(self, user_id, state, cands, hist):
        res = select_action(cands, state, lambda pid: 0.0, epsilon=0.0, rng=self.rng)
        return cands.index(res["selected_plan"])


class EpsGreedyPolicy(Policy):
    """지금 앱의 방식. 사용자별·운동별 보상 평균 + 손 규칙, 확률 epsilon 으로 무작위."""

    def __init__(self, seed: int, epsilon: float = 0.2):
        self.epsilon = epsilon
        self.name = f"eps_greedy_{epsilon:g}"
        super().__init__(seed)
        self.stats: Dict[tuple, List[float]] = {}   # (user, plan) -> [count, total]

    def _avg(self, user_id, plan_id):
        c, t = self.stats.get((user_id, plan_id), (0, 0.0))
        # update_bandit_db 는 평균을 소수 넷째 자리로 반올림해 저장한다
        return round(t / c, 4) if c else 0.0

    def select(self, user_id, state, cands, hist):
        res = select_action(cands, state, lambda pid: self._avg(user_id, pid),
                            epsilon=self.epsilon, rng=self.rng)
        return cands.index(res["selected_plan"])

    def update(self, user_id, state, cands, idx, hist, reward):
        key = (user_id, cands[idx]["plan_id"])
        c, t = self.stats.get(key, (0, 0.0))
        self.stats[key] = [c + 1, t + reward]


class OraclePolicy(Policy):
    """숨은 속성을 아는 기준선. 그 세션 후보 가운데 기대 보상이 가장 큰 것(그날만 본다)."""
    name = "oracle"

    def select(self, user_id, state, cands, hist):
        e = hist["true_expected"]
        return int(np.argmax(e))


# ---------------------------------------------------------------------------
# 특징
# ---------------------------------------------------------------------------
def context_vec(state: Dict) -> np.ndarray:
    lvl = [1.0 if state["experience_level"] == l else 0.0 for l in LEVELS]
    return np.array([1.0, *lvl, state["fatigue"] / 5, state["available_minutes"] / 60,
                     state["recent_adherence_7d"]])


def plan_vec(c: Dict, hist: Dict) -> np.ndarray:
    inten = [1.0 if c["intensity"] == i else 0.0 for i in INTENSITIES]
    parts = set(_split(c["target_parts"]))
    major = [1.0 if p in parts else 0.0 for p in MAJOR_PARTS]
    repeat = sum(1 for pid in hist["recent_plan_ids"] if pid == c["plan_id"]) / 2
    return np.array([*inten, *major, 1.0 if c.get("is_stretching") else 0.0, c["minutes"] / 30,
                     c.get("priority_score", 0) / 100, repeat])


def user_vec(c: Dict) -> np.ndarray:
    """사용자마다 따로 배우는 특징: 강도와 부위. 개인의 체력·선호를 잡으라고 둔다."""
    inten = [1.0 if c["intensity"] == i else 0.0 for i in INTENSITIES]
    parts = set(_split(c["target_parts"]))
    return np.array([*inten, *[1.0 if p in parts else 0.0 for p in MAJOR_PARTS]])


def shared_feats(state, cands, hist) -> np.ndarray:
    cx = context_vec(state)
    return np.stack([np.outer(cx, plan_vec(c, hist)).ravel() for c in cands])


_CTX_DIM = 7     # 1, 숙련도 셋, 피로도, 가용 시간, 최근 순응도
_PLAN_DIM = 15   # 강도 셋, 대분류 부위 여덟, 스트레칭, 시간, 우선순위 점수, 최근 반복
D_SHARED = _CTX_DIM * _PLAN_DIM
D_USER = 11


class LinUCBShared(Policy):
    """모든 사용자가 한 선형 모형을 함께 배운다 (Li et al., WWW 2010 의 Algorithm 1 을 운동 특징 공유로).

    점수 = phi^T theta + alpha * sqrt(phi^T A^-1 phi),  phi = 문맥 특징 (x) 운동 특징.
    """

    def __init__(self, seed: int, alpha: float = 0.3, lam: float = 1.0):
        self.alpha = alpha
        self.name = f"linucb_shared_{alpha:g}"
        super().__init__(seed)
        self.A_inv = np.eye(D_SHARED) / lam
        self.b = np.zeros(D_SHARED)

    def select(self, user_id, state, cands, hist):
        Z = shared_feats(state, cands, hist)
        theta = self.A_inv @ self.b
        s = np.einsum("ij,jk,ik->i", Z, self.A_inv, Z)
        p = Z @ theta + self.alpha * np.sqrt(np.maximum(s, 0))
        return _argmax_random(p, self.rng)

    def update(self, user_id, state, cands, idx, hist, reward):
        z = shared_feats(state, [cands[idx]], hist)[0]
        Az = self.A_inv @ z
        self.A_inv -= np.outer(Az, Az) / (1.0 + z @ Az)     # Sherman-Morrison
        self.b += reward * z


class HybridLinUCB(Policy):
    """공유 모형 + 사용자마다 작은 모형 (Li et al., WWW 2010 의 Algorithm 2, 「운동별」 몫을 「사용자별」로).

    z: 공유 특징(D_SHARED), x: 사용자 특징(D_USER).
    점수 = z^T beta0 + x^T theta_u + alpha * sqrt(s),
    s = z^T A0^-1 z - 2 z^T A0^-1 B_u^T A_u^-1 x + x^T A_u^-1 x + x^T A_u^-1 B_u A0^-1 B_u^T A_u^-1 x.
    tests/test_sim.py 가 이 계산을 [z; x] 를 이은 한 번의 능형 회귀와 맞춰 본다.
    """

    def __init__(self, seed: int, alpha: float = 0.3, lam: float = 1.0):
        self.alpha = alpha
        self.name = f"linucb_hybrid_{alpha:g}"
        super().__init__(seed)
        self.lam = lam
        self.A0 = np.eye(D_SHARED) * lam
        self.A0_inv = np.eye(D_SHARED) / lam
        self.b0 = np.zeros(D_SHARED)
        self.users: Dict[str, dict] = {}

    def _u(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = {"A": np.eye(D_USER) * self.lam, "B": np.zeros((D_USER, D_SHARED)),
                                   "b": np.zeros(D_USER)}
        return self.users[user_id]

    def scores(self, user_id, Z, X):
        u = self._u(user_id)
        Au_inv = np.linalg.inv(u["A"])
        beta0 = self.A0_inv @ self.b0
        theta = Au_inv @ (u["b"] - u["B"] @ beta0)
        C = self.A0_inv @ u["B"].T @ Au_inv                         # (D_SHARED, D_USER)
        Dm = Au_inv @ u["B"] @ self.A0_inv @ u["B"].T @ Au_inv      # (D_USER, D_USER)
        s = (np.einsum("ij,jk,ik->i", Z, self.A0_inv, Z)
             - 2 * np.einsum("ij,jk,ik->i", Z, C, X)
             + np.einsum("ij,jk,ik->i", X, Au_inv, X)
             + np.einsum("ij,jk,ik->i", X, Dm, X))
        mean = Z @ beta0 + X @ theta
        return mean, s

    def select(self, user_id, state, cands, hist):
        Z = shared_feats(state, cands, hist)
        X = np.stack([user_vec(c) for c in cands])
        mean, s = self.scores(user_id, Z, X)
        return _argmax_random(mean + self.alpha * np.sqrt(np.maximum(s, 0)), self.rng)

    def observe(self, user_id, z, x, reward):
        u = self._u(user_id)
        Au_inv = np.linalg.inv(u["A"])
        BtAi = u["B"].T @ Au_inv
        self.A0 += BtAi @ u["B"]
        self.b0 += BtAi @ u["b"]
        u["A"] += np.outer(x, x)
        u["B"] += np.outer(x, z)
        u["b"] += reward * x
        Au_inv = np.linalg.inv(u["A"])
        BtAi = u["B"].T @ Au_inv
        self.A0 += np.outer(z, z) - BtAi @ u["B"]
        self.b0 += reward * z - BtAi @ u["b"]
        self.A0_inv = np.linalg.inv(self.A0)

    def update(self, user_id, state, cands, idx, hist, reward):
        z = shared_feats(state, [cands[idx]], hist)[0]
        self.observe(user_id, z, user_vec(cands[idx]), reward)


def _argmax_random(p: np.ndarray, rng: random.Random) -> int:
    best = np.flatnonzero(p >= p.max() - 1e-12)
    return int(best[rng.randrange(len(best))])


def make_policy(spec: str, seed: int) -> Policy:
    """'random' | 'rule' | 'oracle' | 'eps:0.2' | 'shared:0.3' | 'hybrid:0.3'"""
    kind, _, arg = spec.partition(":")
    if kind == "random":
        return RandomPolicy(seed)
    if kind == "rule":
        return RulePolicy(seed)
    if kind == "oracle":
        return OraclePolicy(seed)
    if kind == "eps":
        return EpsGreedyPolicy(seed, float(arg))
    if kind == "shared":
        return LinUCBShared(seed, float(arg))
    if kind == "hybrid":
        return HybridLinUCB(seed, float(arg))
    raise ValueError(spec)
