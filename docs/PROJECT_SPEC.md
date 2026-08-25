# Adaptive Learning Analytics Platform — Project Spec

## 1. Problem

Traditional quiz platforms treat every student identically: the same questions,
the same order, no adjustment for individual weaknesses. Students who
consistently struggle with a specific topic (e.g. recursion) keep receiving
the same generic material as students who have already mastered it.

## 2. Goal

Build a platform that:
1. Lets students answer topic-tagged questions and records every attempt.
2. Analyzes attempt history to detect per-student, per-topic weaknesses.
3. Uses that analysis to recommend targeted practice material.

## 3. Users

- **Student** — registers, answers questions, sees their own progress.
- **Instructor** (admin) — creates topics/questions, views aggregate class
  analytics.

## 4. Scope (MVP)

In scope for v1:
- User registration/authentication (student + instructor roles)
- Topics and Questions (CRUD, instructor-only write access)
- Attempt tracking: student submits an answer, system records
  correctness, time taken, timestamp
- Basic per-student, per-topic accuracy stats (no ML yet)
- REST API (DRF) covering all of the above

Explicitly **out of scope** for v1 (documented, not forgotten):
- AI-generated recommendations (Gemini integration) — phase 2
- Weakness-detection analytics beyond simple accuracy % — phase 2
- Frontend/dashboard UI — phase 3 (API-first)
- Real-time notifications

## 5. Success criteria for MVP

- A student can register, answer questions across at least 2 topics, and
  retrieve their own accuracy-per-topic via API.
- An instructor can create topics/questions and view all students' attempts.
- Test coverage on core models and endpoints.

## 6. Tech stack

- Backend: Django + Django REST Framework
- Database: PostgreSQL
- Auth: DRF token or JWT (decided in Phase 1 implementation)
- Data (v1): synthetic/seed data via Django management command

## 7. Build order

1. Spec (this document)
2. Repo init + environment
3. Project skeleton (Django project + apps)
4. Config (.env, settings split)
5. Data model (Student, Topic, Question, Attempt)
6. Attempt-tracking API (MVP core)
7. Basic analytics endpoint (accuracy per topic)
8. README + CI
9. Phase 2: AI recommendation layer (Gemini)
