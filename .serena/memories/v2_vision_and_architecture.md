---
name: bodoge-no-mikata v2 Vision and Architecture
description: Simplified, NotebookLM-centric architecture for v2 project
type: project
---

## Project Vision (2026-03-18)

**Core Purpose**: Support board games - know, explain, play (ボードゲームの「知る・説明する・遊ぶ」を支援)

**Key Principles**:
1. Free-thinking simplification and action-orientation
2. Eliminate multi-server management
3. NotebookLM CLI as core (slide generation, video generation, summary sheet generation)
4. Data sources: BGG + official rulebooks ONLY
5. Output quality: Clear, accurate, visual, simple Japanese

**Why**: Single-server complexity removed. Simpler = faster iteration. NotebookLM does heavy lifting for content generation.

## Architecture (v2 - Simplified)

```
📥 Data Ingestion (Local)
├─ BGG API Client (Python, httpx)
├─ Official Rulebook PDF Parser (PyPDF, pdfplumber)
└─ Data cleaning & normalization

💾 Local Storage (Minimal)
├─ SQLite (games.db) - simple schema
└─ JSON backup files

🎬 Core Pipeline (NotebookLM CLI)
├─ Slide generation (from game descriptions)
├─ Video generation (from structured content)
└─ Summary sheet generation (game rules → JP summaries)

🖥️ Frontend (Simple)
└─ Flask or HTML/JS (local-only, no Vercel)
```

## Key Differences from v1

| Aspect | v1 | v2 |
|--------|----|----|
| Primary DB | Supabase PostgreSQL | SQLite (local) |
| Deployment | Vercel serverless | Local Python + Flask |
| Gen tool | Gemini API calls | NotebookLM CLI |
| Server count | 3+ (Vercel, Supabase, Gemini) | 1 (local) |
| Complexity | High (layers, abstractions) | Low (direct, functional) |

## Task Structure (v2)

1. **SQLite Schema & Init** - games.db with minimal fields
2. **BGG Fetcher** - Python TDD implementation
3. **NotebookLM Pipeline** - Integration with CLI tools
4. **Frontend & Verification** - Simple HTML/Flask UI

## Decision Log

- **2026-03-18 09:36**: Chose path B (simplification) over path A (PostgreSQL + multi-server)
- **Rationale**: User emphasis on "自由な発想で単純化と行動化" + NotebookLM CLI as core
- **Stopped**: Team with PostgreSQL setup, BGG Fetcher, E2E tests
- **Preserved**: schema.sql as reference, docker-compose.yml as optional future tool
