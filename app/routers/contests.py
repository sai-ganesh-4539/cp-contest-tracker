import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from app.database import get_db
from app import models, schemas
from app.redis_client import redis_client

router = APIRouter(prefix="/contests", tags=["contests"])

CACHE_TTL = 3600  # 1 hour

@router.get("/", response_model=list[schemas.ContestResponse])
def get_contests(
    platform: Optional[str] = Query(None),
    upcoming: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    cache_key = f"contests:platform={platform}:upcoming={upcoming}"

    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

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

    contests = query.order_by(models.Contest.start_time).all()

    result = [schemas.ContestResponse.model_validate(c).model_dump(mode="json") for c in contests]
    redis_client.set(cache_key, json.dumps(result), ex=CACHE_TTL)

    return result