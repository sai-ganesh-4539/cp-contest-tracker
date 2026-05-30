from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, contests
from app.scheduler import start_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CP Contest Tracker",
    description="Aggregate competitive programming contests across platforms.",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(contests.router)

@app.on_event("startup")
def startup():
    start_scheduler()

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}