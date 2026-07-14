# app/routers/test_email.py
from fastapi import APIRouter, Depends, HTTPException
from app import models
from app.auth import get_current_user
from app.services.email import send_contest_reminder
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(tags=["test"])


@router.post("/test/email-reminder")
def test_email_reminder(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Send a test email to the authenticated user. For testing only."""
    # Find the user's most recent bookmark
    bookmark = (
        db.query(models.Bookmark)
        .filter(models.Bookmark.user_id == current_user.id)
        .order_by(models.Bookmark.created_at.desc())
        .first()
    )

    if not bookmark:
        raise HTTPException(status_code=404, detail="You have no bookmarks to test with")

    contest = bookmark.contest
    print(f"[test] Sending test email to {current_user.email} for '{contest.name}'")
    print(f"[test] Bookmark notified state: {bookmark.notified}")
    print(f"[test] Contest start_time: {contest.start_time}")

    success = send_contest_reminder(
        to_email=current_user.email,
        contest_name=contest.name,
        platform=contest.platform,
        start_time=contest.start_time,
        contest_url=contest.url,
    )

    if success:
        return {
            "status": "sent",
            "to": current_user.email,
            "contest": contest.name,
            "notified_column_exists": True,
        }
    else:
        return {
            "status": "failed",
            "to": current_user.email,
            "contest": contest.name,
            "check_server_logs": True,
        }