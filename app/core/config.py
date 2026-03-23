import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Fitness AI Recommender"
    VERSION: str = "0.1.0"
    DEBUG: bool = True

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    EPSILON: float = 0.2

    COMPLETION_REWARD: float = 1.0
    FAILURE_PENALTY: float = -0.2
    RPE_GOOD_BONUS: float = 0.5
    RPE_HIGH_PENALTY: float = -0.5
    PAIN_PENALTY: float = -1.0
    STREAK_COEF: float = 0.1

    DATABASE_URL: str = "sqlite:///./test.db"

    class Config:
        env_file = ".env"



settings = Settings()