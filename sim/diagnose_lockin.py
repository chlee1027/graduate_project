"""지금 방식(ε-greedy)이 이미 해 본 운동에 묶이는지 잰다: python -m sim.diagnose_lockin [seed]

잰 것
  - 보상이 0 보다 큰 세션의 비율 (안 해 본 운동은 평균 0 으로 시작하므로)
  - 활용(exploitation) 선택 가운데 그 사용자가 이미 해 본 운동을 고른 비율
  - 그 선택 때 후보에 안 해 본 운동이 하나라도 있었던 비율
"""

import sys
import warnings

warnings.filterwarnings("ignore")

import sim.policies as P
from sim import simulator as S


class Probe(P.EpsGreedyPolicy):
    def __init__(self, seed, epsilon=0.2):
        super().__init__(seed, epsilon)
        self.n = self.tried = self.untried_available = 0
        self.rewards = []

    def select(self, user_id, state, cands, hist):
        res = P.select_action(cands, state, lambda pid: self._avg(user_id, pid),
                              epsilon=self.epsilon, rng=self.rng)
        i = cands.index(res["selected_plan"])
        if res["reason"] == "exploitation":
            self.n += 1
            self.tried += (user_id, cands[i]["plan_id"]) in self.stats
            self.untried_available += any((user_id, c["plan_id"]) not in self.stats for c in cands)
        return i

    def update(self, user_id, state, cands, idx, hist, reward):
        self.rewards.append(reward)
        super().update(user_id, state, cands, idx, hist, reward)


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    p = Probe(seed)
    S.run(p, seed, S.SCENARIOS["main"], record_sessions=False)
    pos = sum(r > 0 for r in p.rewards) / len(p.rewards)
    print(f"seed {seed}: 세션 {len(p.rewards)}, 보상 > 0 비율 {pos:.3f}, 활용 선택 {p.n}, "
          f"그 가운데 해 본 운동 {p.tried / p.n:.3f}, 안 해 본 후보가 있었던 비율 {p.untried_available / p.n:.3f}")


if __name__ == "__main__":
    main()
