from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.services.fetcher import fetch_all_contests

scheduler = BackgroundScheduler()

def start_scheduler():
    def job():
        db = SessionLocal()
        try:
            fetch_all_contests(db)
        finally:
            db.close()

    scheduler.add_job(job, "interval", hours=6, id="fetch_contests")
    scheduler.start()
    print("[scheduler] Started — fetching every 6 hours")
    job()