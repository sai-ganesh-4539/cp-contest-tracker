from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.services.fetcher import fetch_all_contests, cleanup_past_contests
from app.redis_client import redis_client

scheduler = BackgroundScheduler()

def start_scheduler():
    def job():
        db = SessionLocal()
        try:
            fetch_all_contests(db)
            cleanup_past_contests(db)
            clear_contests_cache()
        finally:
            db.close()

    scheduler.add_job(job, "interval", hours=6, id="fetch_contests")
    scheduler.start()
    print("[scheduler] Started — fetching every 6 hours")
    job()


def clear_contests_cache():
    keys = redis_client.keys("contests:*")
    if keys:
        redis_client.delete(*keys)
        print(f"[scheduler] Cleared {len(keys)} cached contest keys")