# Adaptive Learning Analytics Platform

A backend platform that tracks how students perform on topic-tagged questions
and surfaces per-topic accuracy analytics — the foundation for adaptive,
personalized practice recommendations.

## Problem

Traditional quiz platforms treat every student identically. This platform
instead records *every* attempt (correct/incorrect, time taken) so that
weak topics can be identified per student, not just guessed at.

## Features

- Token-based authentication with two roles: **student** and **instructor**
- Instructors create topics and multiple-choice questions
- Students submit attempts; correctness is derived server-side (never
  trusted from the client)
- Per-topic accuracy analytics endpoint
- **AI-powered recommendations** (Gemini): topics where a student's
  accuracy falls below a configurable threshold trigger a generated
  explanation and a new targeted practice question, cached per student/topic
- **Dashboard** (`/`): a single-page, dependency-free frontend (vanilla
  HTML/CSS/JS served by Django) showing per-topic accuracy and AI
  recommendations for the signed-in user
- Full REST API (Django REST Framework)
- 27 automated tests covering models, permissions, API behavior,
  the recommendation service (Gemini calls mocked in tests — no real API
  calls or costs incurred during CI), and the dashboard view
- CI pipeline (GitHub Actions) running the full test suite against
  PostgreSQL on every push

## Tech stack

| Layer     | Choice                          |
|-----------|----------------------------------|
| Backend   | Django 6 + Django REST Framework |
| Database  | PostgreSQL                       |
| Auth      | DRF Token Authentication         |
| Testing   | pytest, pytest-django, factory_boy |
| CI        | GitHub Actions                   |

## Project structure

```
config/                 Django project settings, root URLs
apps/
  accounts/              Custom User model (role: student/instructor), auth endpoints
  learning/               Topic, Question, AnswerChoice, Attempt models + API
  analytics/              Aggregate analytics endpoints (per-topic accuracy)
docs/
  PROJECT_SPEC.md         Original scope/requirements document
```

## Getting started

### Prerequisites
- Python 3.12+
- PostgreSQL 16+

### Setup

```bash
git clone <repo-url>
cd adaptive-learning-analytics
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env
# edit .env with your local PostgreSQL credentials

createdb adaptive_learning   # or create it via psql

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Running tests

```bash
pytest -v
```

## API overview

| Method | Endpoint                        | Description                          | Access            |
|--------|----------------------------------|---------------------------------------|--------------------|
| POST   | `/api/auth/register/`           | Create account, returns auth token    | Public             |
| POST   | `/api/auth/login/`               | Obtain auth token                     | Public             |
| GET    | `/api/auth/me/`                  | Current user profile                  | Authenticated      |
| GET/POST | `/api/topics/`                  | List / create topics                  | Read: all, Write: instructor |
| GET/POST | `/api/questions/?topic=<id>`   | List / create questions               | Read: all, Write: instructor |
| POST   | `/api/attempts/`                 | Submit an answer attempt              | Authenticated      |
| GET    | `/api/attempts/`                 | List attempts (own, or all if instructor) | Authenticated |
| GET    | `/api/analytics/topic-accuracy/`| Per-topic accuracy breakdown          | Authenticated      |
| GET    | `/api/analytics/recommendations/`| AI-generated explanation + practice question for each weak topic | Authenticated |

## Configuration notes

- `WEAKNESS_THRESHOLD_PERCENT` (default 50) and `WEAKNESS_MIN_ATTEMPTS`
  (default 3) control weakness detection sensitivity — see `config/settings.py`.
- `GEMINI_API_KEY` must be set in `.env` for the recommendations endpoint
  to work. Get a key from [Google AI Studio](https://aistudio.google.com/apikey).
  Without it, `/api/analytics/recommendations/` will return a
  `generation_errors` entry per weak topic instead of failing outright.

## Roadmap

Phases 1–3 (MVP, AI recommendations, dashboard) are complete. Possible
next steps: instructor-facing class-wide analytics view, spaced-repetition
scheduling, exportable progress reports.

See [`docs/PROJECT_SPEC.md`](docs/PROJECT_SPEC.md) for the full original
scope and design rationale.

## License

MIT
