from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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