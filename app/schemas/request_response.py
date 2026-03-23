from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class OnboardingRequest(BaseModel):
    user_id: str
    age: int
    sex: Literal["male", "female", "other"]
    height_cm: float
    weight_kg: float
    goal: Literal["weight_loss", "muscle_gain", "fitness"]
    experience_level: Literal["beginner", "intermediate", "advanced"]
    injuries: List[str] = []
    weekly_available_days: int
    place_preference: Literal["home", "gym"]
    equipment: List[str] = []


class OnboardingResponse(BaseModel):
    user_id: str
    message: str
    initial_plan: dict


class RecommendRequest(BaseModel):
    user_id: str
    location: Literal["home", "gym"]
    available_minutes: int = Field(..., ge=5, le=120)
    fatigue: int = Field(..., ge=0, le=4)
    sleep_hours: float = Field(..., ge=0, le=24)
    pain_parts: List[str] = []
    equipment_available: List[str] = []
    recent_adherence_7d: float = Field(..., ge=0.0, le=1.0)
    streak: int = Field(..., ge=0)
    avg_rpe_last_7d: float = Field(..., ge=0.0, le=10.0)


class RecommendResponse(BaseModel):
    user_id: str
    state: dict
    candidates: List[dict]
    selected_plan: dict
    reason: str


class LogRequest(BaseModel):
    user_id: str
    plan_id: str
    completed: bool
    actual_minutes: int = 0
    actual_sets: Optional[int] = None
    actual_reps: Optional[int] = None
    rpe: float = Field(..., ge=0.0, le=10.0)
    pain_occurred: bool = False
    user_feedback: Optional[str] = None


class LogResponse(BaseModel):
    message: str
    saved_log: dict


class RewardRequest(BaseModel):
    user_id: str
    completed: bool
    rpe: float
    pain_occurred: bool
    streak: int


class RewardResponse(BaseModel):
    reward: float
    detail: dict