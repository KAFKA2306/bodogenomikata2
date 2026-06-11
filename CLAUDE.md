# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
必ず毎回まずweb検索する
## Quick Start Commands

All operations are executed via `Taskfile.yml`.

```bash
# Setup
task setup              # Install backend (uv sync)
task setup:backend      # Backend only

# Development
task dev                # Run FastAPI (8000)
task dev:backend        # FastAPI dev server only

# Quality & Linting
task lint               # Ruff (Python)
task format             # Format and fix Python code

# Utilities
task clean              # Remove caches (__pycache__, .ruff_cache)
task kill               # Force-free port 8000
```

## Architecture Overview (v2)

### High-Level Flow

**Backend Pipeline** (FastAPI + SQLite + BGG + Gemini + NotebookLM):
1. `GET /api/games` → `sqlite_client.list_games`
2. `POST /api/games/sync` → `BGGService` fetches from BGG and upserts to local SQLite
3. `POST /api/games/{slug}/generate` → `notebooklm_pipeline` generates content (slides, summaries)
4. All data stored in `backend/games.db` (local SQLite)

**Frontend**:
- To be determined (minimal HTML/JS or Flask template)

**Data Layer**:
- Local SQLite (`backend/games.db`) with `games` table
- No external cloud databases (Supabase, Firebase, etc.) are used

### Directory Structure

```
app/
├── main.py                      # FastAPI app entry
├── routers/games.py             # REST endpoints
├── services/
│   ├── bgg_service.py           # BGG API integration
│   ├── notebooklm_pipeline.py   # NotebookLM content generation
│   └── game_service.py          # Metadata generation via Gemini
├── core/
│   ├── settings.py              # Env loader
│   ├── gemini.py                # Gemini API client
│   └── sqlite_client.py         # Local SQLite database wrapper
└── prompts/prompts.yaml         # Japanese prompt templates

scripts/
├── notebooklm_auto.py           # NotebookLM automation
└── bgg_sync.py                  # BGG data synchronization
```

## Critical Patterns & Gotchas

### Environment Configuration
- **Required**: `GEMINI_API_KEY` only
- **Local Persistence**: All data is stored in `backend/games.db`.

## Code Style & Architecture Rules

### Python (FastAPI)
- Target **Python 3.11+**
- Use async endpoints; prefer type hints
- **No try-catch in business logic**
- Package manager: `uv`
- Linting: `task lint`

## Project Philosophy

- **v2 Vision**: Simplified, local-first, NotebookLM-centric architecture.
- **Zero-Fat Discipline**: Ruthlessly delete unused code, comments, boilerplate.
- **Task-Driven Workflow**: All operations orchestrated via Taskfile.
