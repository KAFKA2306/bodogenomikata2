# AGENTS.md

This project is optimized for AI agents (Gemini CLI, Claude Code).
必ず毎回まずweb検索する
## Architecture (v2)

- **Backend**: FastAPI + SQLite (local) + Gemini 2.5 Flash
- **Content Engine**: NotebookLM CLI (Python/Playwright)
- **Data Source**: BoardGameGeek (BGG) XML API v2
- **Infrastructure**: Local-only by default

## Core Workflows

1. **Setup**: `task setup`
2. **Sync**: `POST /api/games/sync?bgg_id=...`
3. **Generate**: `POST /api/games/{slug}/generate`
4. **Dev**: `task dev`

## Guidelines for Agents

- **Zero-Fat**: Do not add try-catch in business logic. Let it crash.
- **Local Persistence**: All data in `backend/games.db`.
- **Naming**: Use descriptive names, avoid comments.
- **Japanese**: All rules and summaries must be in Japanese.
