# app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.services.fetcher import fetch_all_contests, cleanup_past_contests
from app.services.email import send_contest_reminder
from app.redis_client import redis_client
from app import models
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()

# Window: send reminder if contest starts in this range (50 to 70 minutes from now)
REMINDER_WINDOW_MIN_LOW = 50
REMINDER_WINDOW_MIN_HIGH = 70


def start_scheduler():
    def fetch_job():
        db = SessionLocal()
        try:
            try:
                fetch_all_contests(db)
            except Exception as e:
                print(f"[scheduler] fetch_all_contests failed: {e}")
            try:
                cleanup_past_contests(db)
            except Exception as e:
                print(f"[scheduler] cleanup_past_contests failed: {e}")
            try:
                clear_contests_cache()
            except Exception as e:
                print(f"[scheduler] clear_contests_cache failed: {e}")
        finally:
            db.close()

    def reminder_job():
        """Send email reminders for contests starting in ~1 hour."""
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            window_low = now + timedelta(minutes=REMINDER_WINDOW_MIN_LOW)
            window_high = now + timedelta(minutes=REMINDER_WINDOW_MIN_HIGH)

            # Find bookmarks where contest starts in the next 50-70 min and not yet notified
            bookmarks = (
                db.query(models.Bookmark)
                .join(models.Contest, models.Bookmark.contest_id == models.Contest.id)
                .filter(models.Bookmark.notified == False)
                .filter(models.Contest.start_time >= window_low)
                .filter(models.Contest.start_time <= window_high)
                .all()
            )

            if not bookmarks:
                return

            print(f"[reminder] Found {len(bookmarks)} bookmark(s) to remind")

            for bm in bookmarks:
                contest = bm.contest
                user = bm.user
                if not user or not contest:
                    continue

                success = send_contest_reminder(
                    to_email=user.email,
                    contest_name=contest.name,
                    platform=contest.platform,
                    start_time=contest.start_time,
                    contest_url=contest.url,
                )

                if success:
                    bm.notified = True
                    db.commit()
                    print(f"[reminder] Marked notified: bookmark {bm.id}")
                else:
                    print(f"[reminder] Failed to send for bookmark {bm.id} — will retry next run")
        except Exception as e:
            print(f"[reminder] Job failed: {e}")
        finally:
            db.close()

    scheduler.add_job(fetch_job, "interval", hours=6, id="fetch_contests")
    scheduler.add_job(reminder_job, "interval", minutes=5, id="send_reminders")
    scheduler.start()
    print("[scheduler] Started — fetching every 6h, reminders every 5min")
    fetch_job()


def clear_contests_cache():
    keys = redis_client.keys("contests:*")
    if keys:
        redis_client.delete(*keys)
        print(f"[scheduler] Cleared {len(keys)} cached contest keys")