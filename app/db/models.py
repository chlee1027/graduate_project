from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    age = Column(Integer, nullable=False)
    sex = Column(String, nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    goal = Column(String, nullable=False)
    experience_level = Column(String, nullable=False)
    injuries = Column(Text, nullable=True)      # JSON 대신 우선 문자열 저장
    weekly_available_days = Column(Integer, nullable=False)
    place_preference = Column(String, nullable=False)
    equipment = Column(Text, nullable=True)     # JSON 대신 우선 문자열 저장
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ExercisePlan(Base):
    __tablename__ = "exercise_plans"

    plan_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)  # home, gym
    type = Column(String, nullable=False)      # rep-based, time-based
    required_equipment = Column(Text, nullable=True)  # Comma separated
    target_parts = Column(Text, nullable=False)       # Comma separated
    avoid_if_pain = Column(Text, nullable=True)       # Comma separated
    intensity = Column(String, nullable=False) # low, medium, high
    minutes = Column(Integer, nullable=False)  # Total base minutes
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    target_rpe = Column(Integer, nullable=True)  # Recommended RPE (1-10)
    rest_seconds = Column(Integer, default=60)   # Recommended rest time
    met_value = Column(Float, default=3.0)       # Metabolic Equivalent of Task
    is_stretching = Column(Boolean, default=False)
    video_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    state_json = Column(Text, nullable=False)
    selected_plan_json = Column(Text, nullable=False)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recommendation_id = Column(String, ForeignKey("recommendations.recommendation_id"), nullable=False)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    plan_id = Column(String, ForeignKey("exercise_plans.plan_id"), nullable=False)
    completed = Column(Boolean, nullable=False)
    actual_minutes = Column(Integer, default=0)
    actual_sets = Column(Integer, nullable=True)
    actual_reps = Column(Integer, nullable=True)
    rpe = Column(Float, nullable=False)
    pain_occurred = Column(Boolean, default=False)
    user_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BanditStat(Base):
    __tablename__ = "bandit_stats"
    __table_args__ = (
        UniqueConstraint("user_id", "plan_id", name="uq_user_plan"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    plan_id = Column(String, ForeignKey("exercise_plans.plan_id"), nullable=False)
    count = Column(Integer, default=0, nullable=False)
    total_reward = Column(Float, default=0.0, nullable=False)
    avg_reward = Column(Float, default=0.0, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())