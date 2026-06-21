# CP Contest Tracker

A backend API that aggregates upcoming competitive programming contests from Codeforces, LeetCode, CodeChef, and AtCoder into a single unified feed. Users can register, browse contests, and bookmark the ones they plan to attend.

## Features

- JWT authentication (register + login)
- Contest feed aggregated across multiple platforms
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
| Cache + Rate limiting | Redis 7 |
| Auth | JWT (python-jose) |
| Background jobs | APScheduler |
| Containers | Docker + Docker Compose |
| Deployment | GCP Cloud Run + Cloud SQL + Memorystore |

## Getting Started

```bash
git clone https://github.com/Learner12313/cp-contest-tracker.git
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
│   └── models.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Live Demo

🔗 [https://cp-contest-tracker-510u.onrender.com/docs](https://cp-contest-tracker-510u.onrender.com/docs)

## Roadmap

- [x] Phase 1 — Project scaffold
- [x] Phase 2 — JWT auth
- [x] Phase 3 — Contest ingestion + scheduler
- [x] Phase 4 — Bookmarks
- [x] Phase 5 — Redis caching + rate limiting
- [x] Phase 6 — Deployment (Render)
