from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(tags=["bookmarks"])

@router.post("/contests/{contest_id}/bookmark", status_code=201)
def bookmark_contest(
    contest_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    contest = db.query(models.Contest).filter(models.Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    existing = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id,
        models.Bookmark.contest_id == contest_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already bookmarked")

    bookmark = models.Bookmark(user_id=current_user.id, contest_id=contest_id)
    db.add(bookmark)
    db.commit()
    return {"detail": "Bookmarked"}


@router.delete("/contests/{contest_id}/bookmark", status_code=204)
def remove_bookmark(
    contest_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    bookmark = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id,
        models.Bookmark.contest_id == contest_id,
    ).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    db.delete(bookmark)
    db.commit()
    return None


@router.get("/me/bookmarks", response_model=list[schemas.BookmarkResponse])
def get_my_bookmarks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id
    ).all()