from fastapi import FastAPI
from app.routers import onboarding, recommend, log, reward
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fitness AI Recommender")

app.include_router(onboarding.router, prefix="/api/onboarding", tags=["onboarding"])
app.include_router(recommend.router, prefix="/api/recommend", tags=["recommend"])
app.include_router(log.router, prefix="/api/log", tags=["log"])
app.include_router(reward.router, prefix="/api/reward", tags=["reward"])


@app.get("/")
def root():
    return {"message": "Fitness AI backend is running"}