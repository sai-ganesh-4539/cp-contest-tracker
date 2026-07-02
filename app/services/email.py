# app/services/email.py
import os
import httpx
from datetime import datetime


RESEND_API_URL = "https://api.resend.com/emails"


def send_contest_reminder(
    to_email: str,
    contest_name: str,
    platform: str,
    start_time: datetime,
    contest_url: str | None,
) -> bool:
    """Send a contest reminder email via Resend. Returns True on success."""
    api_key = os.environ.get("RESEND_API_KEY", "").strip()
    from_email = os.environ.get(
        "FROM_EMAIL", "CP Tracker <onboarding@resend.dev>"
    ).strip()

    if not api_key:
        print("[email] RESEND_API_KEY not set — skipping")
        return False

    start_str = start_time.strftime("%a, %b %d at %H:%M UTC")
    subject = f"⏰ Starting soon: {contest_name}"

    button_html = (
        f"<a href='{contest_url}' style='display: inline-block; background: #0f172a; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-size: 14px; font-weight: 500; margin-top: 8px;'>Go to contest →</a>"
        if contest_url
        else ""
    )

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 560px; margin: 0 auto; padding: 24px; color: #0f172a;">
      <h2 style="margin: 0 0 8px 0; font-size: 20px;">⏰ Your contest starts in ~1 hour</h2>
      <p style="margin: 0 0 16px 0; color: #475569; font-size: 14px;">You bookmarked this contest on CP Contest Tracker.</p>
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin: 16px 0;">
        <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">{platform}</div>
        <div style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">{contest_name}</div>
        <div style="font-size: 14px; color: #475569;"><strong>Starts:</strong> {start_str}</div>
      </div>
      {button_html}
      <p style="margin-top: 24px; font-size: 12px; color: #94a3b8;">Sent by CP Contest Tracker.</p>
    </div>
    """

    payload = {"from": from_email, "to": [to_email], "subject": subject, "html": html}

    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(
                RESEND_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        if res.status_code == 200:
            print(f"[email] Sent reminder to {to_email} for '{contest_name}'")
            return True
        else:
            print(f"[email] Resend error {res.status_code}: {res.text}")
            return False
    except Exception as e:
        print(f"[email] Failed to send to {to_email}: {e}")
        return False