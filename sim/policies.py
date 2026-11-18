"""비교할 추천 방식들. 모두 select(user_id, state, candidates, hist) -> 고른 후보의 번호.

hist["true_expected"] 는 숨은 속성으로 계산한 기대 보상이다. Oracle 만 쓰고 나머지는 보지 않는다.
"""

from __future__ import annotations

import random
from typing import Dict, List

import numpy as np

from app.services import linucb as L
from app.services.linucb import D_SHARED, D_USER
from app.services.recommender_bandit_db import select_action



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
# LinUCB: 특징과 hybrid 계산은 앱과 같은 app/services/linucb.py 를 쓴다
# ---------------------------------------------------------------------------
def shared_feats(state, cands, hist) -> np.ndarray:
    return L.shared_feats(state, cands, hist["recent_plan_ids"])


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
    """공유 모형 + 사용자마다 작은 모형. 앱의 추천 엔진과 같은 계산(app/services/linucb.py).

    balance 는 코치 점수(최근 덜 한 부위일수록 큼)에 거는 고정 가중치다. 0 이면 보상만 본다.
    """

    def __init__(self, seed: int, alpha: float = 0.3, balance: float = 0.0, lam: float = 1.0):
        self.alpha, self.balance, self.lam = alpha, balance, lam
        self.name = f"linucb_hybrid_{alpha:g}" + (f"_bal{balance:g}" if balance else "")
        super().__init__(seed)
        self.shared = L.SharedState(lam=lam)
        self.A0_inv = np.linalg.inv(self.shared.A0)
        self.users: Dict[str, L.UserState] = {}

    def _u(self, user_id) -> L.UserState:
        if user_id not in self.users:
            self.users[user_id] = L.UserState(lam=self.lam)
        return self.users[user_id]

    def scores(self, user_id, Z, X):
        return L.scores(self.shared, self._u(user_id), Z, X, self.A0_inv)

    def select(self, user_id, state, cands, hist):
        res = L.select(self.shared, self._u(user_id), state, cands, hist["recent_plan_ids"],
                       self.alpha, self.balance, rng=self.rng, A0_inv=self.A0_inv)
        return res["index"]

    def observe(self, user_id, z, x, reward):
        L.observe(self.shared, self._u(user_id), z, x, reward)
        self.A0_inv = np.linalg.inv(self.shared.A0)

    def update(self, user_id, state, cands, idx, hist, reward):
        z, x = L.features_for(state, cands[idx], hist["recent_plan_ids"])
        self.observe(user_id, z, x, reward)


def _argmax_random(p: np.ndarray, rng: random.Random) -> int:
    best = np.flatnonzero(p >= p.max() - 1e-12)
    return int(best[rng.randrange(len(best))])


def make_policy(spec: str, seed: int) -> Policy:
    """'random' | 'rule' | 'oracle' | 'eps:0.2' | 'shared:0.3' | 'hybrid:0.3' | 'hybrid:1:0.5'(alpha:균형 가중치)"""
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
        alpha, _, bal = arg.partition(":")
        return HybridLinUCB(seed, float(alpha), float(bal or 0))
    raise ValueError(spec)
