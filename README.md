# English Learning Platform

**Structured English practice for learners in Vietnam.**

## Project Overview

English Learning Platform is an independent web application being built for people in Vietnam who want to improve their English through regular, guided practice. The planned study flow will help learners choose their next lesson, act on feedback, and revisit material when it is due for review.

The repository currently contains a runnable development foundation. The web home page checks its connection to the API, and the local stack provides database migrations, health checks, and automated tests. Learner accounts, lessons, and progress tracking are planned.

## Product Vision

Help learners build a sustainable study habit through short, mobile-friendly sessions, Vietnamese guidance, and a progression aligned with the Common European Framework of Reference for Languages (CEFR). The initial path starts at A1. Practice feedback, saved progress, and scheduled review will help learners decide what to work on next.

## Key Features

All learning capabilities below are **planned**. The implemented foundation is listed under [Current Project Status](#current-project-status).

| Capability | Target experience | Milestone |
| --- | --- | --- |
| Structured learning roadmaps | Follow an A1 path organized into courses, units, and lessons, with higher levels added as content is approved. | MVP |
| Interactive sentence typing | Type words, phrases, and sentences, see targeted feedback, and resume a lesson at the selected difficulty. | MVP |
| Vocabulary and flashcards | Study curated decks and keep vocabulary from completed lessons in a personal collection. | MVP |
| Spaced repetition | Opt vocabulary into scheduled review and rate how well it was recalled. | MVP |
| Personalized learning dashboard | Resume the next lesson, set a daily study goal, and see due reviews. | MVP |
| Learning progress tracking | Record lesson completion, study activity, and practice results across sessions. | MVP |
| Content management system | Import and edit lessons, review them, and publish versioned content. | MVP |
| Grammar practice | Read explanations and apply them in exercises with feedback. | V1 |
| Reading and translation | Read bilingual texts and practice translating against curated references and rubrics. | V1 |
| Listening and video learning | Practice with audio and video lessons, synchronized captions, and quizzes where available. | V1 |
| Dictation and shadowing | Transcribe short clips and compare locally recorded speech with a model. | V1 |
| Pronunciation practice | Study IPA sounds and use audio examples and minimal-pair listening exercises. | V1 |
| AI-powered learning assistance | Request opt-in feedback on supported activities, subject to quality and privacy checks. | V2 |

## Technology Stack

| Layer | Technologies in the repository |
| --- | --- |
| Web | Next.js App Router, React, TypeScript, Tailwind CSS, Node.js 24, npm 11 workspaces |
| API | Python 3.13, FastAPI, Pydantic, SQLAlchemy, psycopg, uv |
| Database | PostgreSQL 17 and Alembic |
| API contracts | OpenAPI 3.1 and generated TypeScript types |
| Testing and automation | pytest, Ruff, ESLint, Node.js test runner, Playwright, Docker Compose, GitHub Actions |

## System Architecture

The monorepo contains a Next.js frontend and a single FastAPI service backed by PostgreSQL. The browser calls the API through the web origin. Next.js forwards operational health checks and requests under `/api/v1/` to FastAPI. Docker Compose starts PostgreSQL, applies migrations, then starts the API and web services.

The API exposes `/health/live` for process liveness, `/health/ready` for database connectivity and the expected Alembic revision, and `/api/v1/openapi.json` for the current API contract. The target architecture organizes future product domains within a modular monolith. [Architecture overview](docs/architecture/01-system-architecture.md)

## Project Structure

```text
apps/
  web/                 Next.js application, generated API types, and web tests
  api/                 FastAPI application, Alembic migrations, and API tests
docs/                  Product requirements, architecture, roadmap, and test plans
.github/workflows/     GitHub Actions workflow
compose.yaml           Local PostgreSQL, migration, API, and web services
.env.example           Local Compose configuration template
```

## Getting Started

Install Docker Engine with Docker Compose v2 or later. For host-side development and testing, install Node.js 24 with npm 11, Python 3.13, and uv 0.12.7. Run the commands from the repository root. The examples use PowerShell. On Linux and macOS, use `npm` in place of `npm.cmd` and adapt the shell syntax for environment variables.

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
docker compose config --quiet
docker compose up --build --detach --wait
Invoke-RestMethod http://127.0.0.1:3000/health/live
Invoke-RestMethod http://127.0.0.1:3000/health/ready
```

With the default ports, open the local web app at `http://127.0.0.1:3000/`. The OpenAPI document is at `http://127.0.0.1:3000/api/v1/openapi.json`. Run `docker compose down` to stop the stack and retain the database volume.

## Environment Configuration

Use [`.env.example`](.env.example) as the template for your local `.env`. Keep database credentials in local configuration. Use a URL-safe PostgreSQL password for the Compose setup.

| Setting | Purpose |
| --- | --- |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Configure the local PostgreSQL service. |
| `POSTGRES_PORT`, `API_PORT`, `WEB_PORT` | Set loopback host ports. Defaults are `15432`, `8000`, and `3000`, respectively. |
| `DATABASE_URL` | SQLAlchemy connection URL with the `postgresql+psycopg://` scheme. Compose sets it for the API and migration services. Set it in the API terminal when running directly on the host. |
| `TEST_DATABASE_URL` | Connection URL for a disposable PostgreSQL database used by integration tests. |
| `API_INTERNAL_URL` | API origin used by Next.js rewrites. Set it before starting the dev server or building the web app if the host API runs outside the default origin `http://127.0.0.1:8000`. Use an origin without credentials or a path. |
| `PLAYWRIGHT_BASE_URL` | Web origin for tests against a running stack. Set it explicitly when testing Compose. |

## Development Commands

For host-side development, stop the Compose web and API services to free their ports, leave PostgreSQL running, and install the frontend dependencies.

```powershell
docker compose stop web api
docker compose up --detach --wait db
npm.cmd ci
```

In an API terminal, load the PostgreSQL settings from `.env` and apply migrations before starting Uvicorn. The parser below assumes the simple `KEY=VALUE` format used by the template.

```powershell
$db = Get-Content -Raw -LiteralPath .env | ConvertFrom-StringData
$dbOrigin = "postgresql+psycopg://$($db.POSTGRES_USER):$($db.POSTGRES_PASSWORD)@127.0.0.1:$($db.POSTGRES_PORT)"
$env:DATABASE_URL = "$dbOrigin/$($db.POSTGRES_DB)"
Set-Location apps/api
uv sync --locked
uv run --locked alembic upgrade head
uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

In a separate terminal at the repository root, run `npm.cmd run dev`.

## Testing & Quality Assurance

Run the frontend checks from the repository root after `npm.cmd ci`. Start the Compose stack before the browser tests. Adjust the base URL if you changed the web port.

```powershell
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run test:web
npm.cmd run build
npm.cmd exec --workspace @elp/web -- playwright install chromium
$env:PLAYWRIGHT_BASE_URL = 'http://127.0.0.1:3000'
npm.cmd run test:e2e
```

For the backend suite, run the following from the repository root with the database service running. Create `elp_test` once and use a disposable test database because the suite applies and reverses migrations.

```powershell
$db = Get-Content -Raw -LiteralPath .env | ConvertFrom-StringData
$dbOrigin = "postgresql+psycopg://$($db.POSTGRES_USER):$($db.POSTGRES_PASSWORD)@127.0.0.1:$($db.POSTGRES_PORT)"
docker compose exec -T db createdb -U $db.POSTGRES_USER elp_test
$env:DATABASE_URL = "$dbOrigin/$($db.POSTGRES_DB)"
$env:TEST_DATABASE_URL = "$dbOrigin/elp_test"
Push-Location apps/api
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked alembic upgrade head
uv run --locked alembic check
uv run --locked python -m pytest
uv run --locked python -m app.export_openapi --output openapi.json
Pop-Location
npm.cmd run api:types
git diff --exit-code -- apps/api/openapi.json apps/web/lib/api/schema.d.ts
```

Recorded local verification covers 10 backend tests, 4 web unit tests, and 4 Playwright smoke tests. The GitHub Actions workflow defines quality checks for pushes and pull requests. [Local verification record](docs/testing/04-sprint-00-verification.md) · [CI workflow](.github/workflows/ci.yml)

## Development Roadmap

| Milestone | Scope | Status |
| --- | --- | --- |
| Development foundation | Local stack, baseline migration, API contracts, and automated checks | Implemented |
| MVP | Email verification and onboarding, A1 curriculum, core practice and review flows, and editorial publishing | Planned |
| V1 | Additional language skills, bilingual content, and media-based practice | Planned |
| V2 | Opt-in AI feedback and expanded personalization | Planned |

Email authentication and onboarding are the next scheduled work. [Full roadmap](docs/plans/00-master-roadmap.md)

## Documentation

- [Product requirements](docs/requirements/01-PRD.md) and [software requirements](docs/requirements/02-SRS.md)
- [System architecture](docs/architecture/01-system-architecture.md) and [local toolchain decisions](docs/architecture/adr/0001-local-toolchain-and-monorepo.md)
- [Database design](docs/architecture/04-database-design.md) and [target API specification](docs/architecture/05-api-specification.md)
- [Testing strategy](docs/testing/01-test-strategy.md) and [development roadmap](docs/plans/00-master-roadmap.md)

## Current Project Status

The current implementation supports a responsive home page with a live API connectivity check and retry, database-aware readiness, a baseline migration, and generated API types. This is a development preview. The first learner-facing milestone is the MVP described above.
