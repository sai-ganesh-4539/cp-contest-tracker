# app/migrate_notified.py
"""One-time migration: add 'notified' column to bookmarks table."""
from app.database import engine
from sqlalchemy import text


def run():
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='bookmarks' AND column_name='notified'"
        ))
        if result.fetchone():
            print("[migrate] 'notified' column already exists — skipping")
            return

        print("[migrate] Adding 'notified' column to bookmarks...")
        conn.execute(text(
            "ALTER TABLE bookmarks ADD COLUMN notified BOOLEAN NOT NULL DEFAULT false"
        ))
        conn.commit()
        print("[migrate] Done")


if __name__ == "__main__":
    run()