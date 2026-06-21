# CP Contest Tracker

A backend API that aggregates upcoming competitive programming contests from Codeforces, LeetCode, CodeChef, AtCoder, and 50+ other platforms via CLIST into a single unified feed. Users can register, browse contests, and bookmark the ones they plan to attend.

## Live Demo

🔗 [https://cp-contest-tracker-510u.onrender.com/docs](https://cp-contest-tracker-510u.onrender.com/docs)

Note: hosted on Render's free tier — the service spins down after periods of inactivity, so the first request may take 30-50 seconds to wake it up.

## Features

- JWT authentication (register + login)
- Contest feed aggregated across multiple platforms (Codeforces API + CLIST.by)
- Filter by platform or upcoming window (next 7 days)
- Bookmark contests per user
- Redis caching on contest list (1hr TTL)
- Redis rate limiting on bookmark actions (10/hr per user)
- Background scheduler fetches fresh data every 6 hours

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| Database | PostgreSQL 16 |
| Cache + Rate limiting | Redis |
| Auth | JWT (python-jose) |
| Background jobs | APScheduler |
| Containers | Docker + Docker Compose |
| Deployment | Render (Web Service + managed PostgreSQL + Key Value/Redis) |

## Getting Started

```bash
git clone https://github.com/sai-ganesh-4539/cp-contest-tracker.git
cd cp-contest-tracker
cp .env.example .env
docker compose up --build
```

Docs at `http://localhost:8000/docs`

## Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Register |
| POST | `/auth/login` | No | Login, returns JWT |
| GET | `/contests` | No | List contests |
| GET | `/contests?platform=` | No | Filter by platform |
| GET | `/contests?upcoming=true` | No | Next 7 days |
| POST | `/contests/{id}/bookmark` | Yes | Bookmark |
| DELETE | `/contests/{id}/bookmark` | Yes | Remove bookmark |
| GET | `/me/bookmarks` | Yes | Your bookmarks |
| GET | `/health` | No | Health check |

## Project Structure

```
cp-contest-tracker/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── scheduler.py
│   ├── redis_client.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── contests.py
│   │   └── bookmarks.py
│   └── services/
│       └── fetcher.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Roadmap

- [x] Phase 1 — Project scaffold
- [x] Phase 2 — JWT auth
- [x] Phase 3 — Contest ingestion + scheduler
- [x] Phase 4 — Bookmarks
- [x] Phase 5 — Redis caching + rate limiting
- [x] Phase 6 — Deployment (Render)