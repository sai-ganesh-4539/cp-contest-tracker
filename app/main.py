from fastapi import FastAPI
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CP Contest Tracker",
    description="Aggregate competitive programming contests across platforms.",
    version="0.1.0",
)

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}