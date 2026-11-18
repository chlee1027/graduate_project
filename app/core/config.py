from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 추천 엔진: "hybrid" (hybrid LinUCB, docs/simulation_eval.md) 또는 "eps_greedy" (예전 방식)
    RECOMMENDER: str = "hybrid"
    LINUCB_ALPHA: float = 1.0
    LINUCB_LAMBDA: float = 1.0
    BALANCE_WEIGHT: float = 0.25  # 코치 점수(최근 덜 한 부위) 가중치. 조율 근거는 docs/simulation_eval.md 6.6절
    EPSILON: float = 0.2

    COMPLETION_REWARD: float = 1.0
    FAILURE_PENALTY: float = 0.0
    RPE_GOOD_BONUS: float = 0.5
    RPE_HIGH_PENALTY: float = -0.5
    PAIN_PENALTY: float = -1.0
    STREAK_COEF: float = 0.1

    DATABASE_URL: str = "postgresql://postgres:1234@localhost:5432/fitness_ai"
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()