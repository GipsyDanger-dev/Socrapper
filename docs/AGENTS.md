# AGENTS.md — Socrapper Project Guide

## gstack

Use the `/browse` skill from gstack for all web browsing, never use `mcp__claude-in-chrome__*` tools.

Available gstack skills:
- `/browse` — Fast headless browser for QA testing and site dogfooding
- `/office-hours` — Office hours
- `/plan-ceo-review` — CEO review planning
- `/plan-eng-review` — Engineering review planning
- `/plan-design-review` — Design review planning
- `/design-consultation` — Design consultation
- `/design-shotgun` — Design shotgun
- `/design-html` — HTML design
- `/review` — Code review
- `/ship` — Ship code
- `/land-and-deploy` — Land and deploy
- `/canary` — Canary deployment
- `/benchmark` — Performance benchmarking
- `/connect-chrome` — Connect Chrome
- `/qa` — QA testing
- `/qa-only` — QA only
- `/design-review` — Design review
- `/setup-browser-cookies` — Setup browser cookies
- `/setup-deploy` — Setup deployment
- `/setup-gbrain` — Setup gbrain
- `/retro` — Retrospective
- `/investigate` — Investigation and debugging
- `/document-release` — Document release
- `/document-generate` — Generate documentation
- `/codex` — Codex
- `/cso` — CSO
- `/autoplan` — Auto planning
- `/plan-devex-review` — DevEx review planning
- `/devex-review` — DevEx review
- `/careful` — Careful mode
- `/freeze` — Freeze
- `/guard` — Guard
- `/unfreeze` — Unfreeze
- `/gstack-upgrade` — Upgrade gstack
- `/learn` — Learn

## Project Overview

Socrapper is a general internet sentiment scraper built with Django + Scrapling backend and React 18 frontend.

- **Backend**: Django 4.2 + Django REST Framework, Scrapling for web scraping
- **Frontend**: React 18 + Vite 4 + Chart.js
- **Database**: Supabase PostgreSQL (or SQLite for local dev)
- **LLM**: OpenAI-compatible API for AI analysis

## Key Commands

```bash
# Start backend
python manage.py runserver 8000

# Start frontend (separate terminal)
npm run dev

# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations scraper
```

## API Endpoints (14 total)

All under `/api/`:
- `POST /scrape` — Scrape platform
- `POST /analyze` — Sentiment analysis
- `GET /platforms` — List platforms
- `POST /export` — Export CSV
- `GET /exports` — List exports
- `GET /scrape-history` — History (paginated)
- `POST /surf` — Full surf
- `POST /surf/quick` — Quick search
- `POST /surf/deep` — Deep surf
- `POST /surf/extract` — Extract URL
- `POST /surf/ai-analyze` — AI analysis

## Environment

- `.env` — Database, LLM, Django secret key
- `DB_ENGINE` — sqlite / postgresql / mysql

## Git Rules

- Push to GitHub every 3 file changes
- Never use co-author
- Commit message format: short descriptive summary in English