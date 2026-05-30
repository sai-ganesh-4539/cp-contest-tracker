from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/contests", tags=["contests"])

@router.get("/", response_model=list[schemas.ContestResponse])
def get_contests(
    platform: Optional[str] = Query(None),
    upcoming: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Contest)

    if platform:
        query = query.filter(models.Contest.platform == platform.lower())

    if upcoming:
        now = datetime.utcnow()
        week = now + timedelta(days=7)
        query = query.filter(
            models.Contest.start_time >= now,
            models.Contest.start_time <= week,
        )

    return query.order_by(models.Contest.start_time).all()