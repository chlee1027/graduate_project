from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import onboarding, recommend, log, reward, user, debug
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fitness AI Recommender")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(onboarding.router, prefix="/api/onboarding", tags=["onboarding"])
app.include_router(recommend.router, prefix="/api/recommend", tags=["recommend"])
app.include_router(log.router, prefix="/api/log", tags=["log"])
app.include_router(reward.router, prefix="/api/reward", tags=["reward"])
app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(debug.router, prefix="/api/debug", tags=["debug"])


@app.get("/")
def root():
    return {"message": "Fitness AI backend is running"}