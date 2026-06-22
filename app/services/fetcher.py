import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from app import models
from app.config import settings

CODEFORCES_URL = "https://codeforces.com/api/contest.list"
CLIST_URL = "https://clist.by/api/v2/contest/"

def fetch_codeforces(db: Session):
    try:
        resp = httpx.get(CODEFORCES_URL, timeout=10)
        data = resp.json()
        if data["status"] != "OK":
            return
        now = datetime.utcnow().timestamp()
        for c in data["result"]:
            if c["phase"] != "BEFORE":
                continue
            start_time = datetime.utcfromtimestamp(c["startTimeSeconds"])
            duration_minutes = c["durationSeconds"] // 60
            existing = db.query(models.Contest).filter(
                models.Contest.platform == "codeforces",
                models.Contest.external_id == str(c["id"])
            ).first()
            if existing:
                existing.name = c["name"]
                existing.start_time = start_time
                existing.duration_minutes = duration_minutes
                existing.fetched_at = datetime.utcnow()
            else:
                contest = models.Contest(
                    platform="codeforces",
                    name=c["name"],
                    start_time=start_time,
                    duration_minutes=duration_minutes,
                    url=f"https://codeforces.com/contest/{c['id']}",
                    external_id=str(c["id"]),
                )
                db.add(contest)
        db.commit()
    except Exception as e:
        print(f"[fetcher] Codeforces error: {e}")


def fetch_clist(db: Session):
    if not settings.clist_api_key:
        print("[fetcher] No CLIST_API_KEY set, skipping")
        return
    try:
        username = settings.clist_api_key.split(":")[0]
        api_key = settings.clist_api_key.split(":")[1]
        params = {
            "username": username,
            "api_key": api_key,
            "upcoming": "true",
            "order_by": "start",
            "limit": 100,
            "format": "json",
        }
        resp = httpx.get(CLIST_URL, params=params, timeout=10)
        data = resp.json()
        for c in data.get("objects", []):
            platform = c["resource"].split(".")[0].lower()
            if platform == "codeforces":
                continue
            start_time = datetime.strptime(c["start"], "%Y-%m-%dT%H:%M:%S")
            end_time = datetime.strptime(c["end"], "%Y-%m-%dT%H:%M:%S")
            duration_minutes = int((end_time - start_time).total_seconds() // 60)
            existing = db.query(models.Contest).filter(
                models.Contest.platform == platform,
                models.Contest.external_id == str(c["id"])
            ).first()
            if existing:
                existing.name = c["event"]
                existing.start_time = start_time
                existing.duration_minutes = duration_minutes
                existing.fetched_at = datetime.utcnow()
            else:
                contest = models.Contest(
                    platform=platform,
                    name=c["event"],
                    start_time=start_time,
                    duration_minutes=duration_minutes,
                    url=c["href"],
                    external_id=str(c["id"]),
                )
                db.add(contest)
        db.commit()
    except Exception as e:
        print(f"[fetcher] CLIST error: {e}")


def fetch_all_contests(db: Session):
    print("[fetcher] Fetching contests...")
    fetch_codeforces(db)
    fetch_clist(db)
    print("[fetcher] Done.")

def cleanup_past_contests(db: Session):
    """Delete contests that have already ended (start_time + duration < now)."""
    from datetime import timedelta
    now = datetime.utcnow()
    contests = db.query(models.Contest).all()
    deleted = 0
    for c in contests:
        if not c.duration_minutes:
            continue
        end_time = c.start_time + timedelta(minutes=c.duration_minutes)
        if end_time < now:
            db.delete(c)
            deleted += 1
    if deleted:
        db.commit()
        print(f"[fetcher] Cleaned up {deleted} past contests")