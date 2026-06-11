---
name: v2 Implementation Status
description: Current state of bodoge-no-mikata v2 core components
type: project
---

## Completed Components ✅

### 1. BGG Fetcher (100% Test Coverage)
- **File**: `backend/app/services/bgg_fetcher.py` (90 lines)
- **Features**: Async BGG API client with XML parsing
- **Tests**: 5 unit tests, 100% coverage
- **Status**: ✅ Ready for use

### 2. BGG Mapper  
- **File**: `backend/app/utils/bgg_mapper.py` (64 lines)
- **Features**: Converts BGG API response to games schema
- **Tests**: 7 tests, 100% coverage
- **Status**: ✅ Ready for use

### 3. BGG Service
- **File**: `backend/app/services/bgg_service.py` (47 lines)
- **Features**: Orchestrates fetch + upsert
- **Tests**: 5 tests, 100% coverage
- **⚠️ Issue**: Still references `app.core.supabase` - needs SQLite update
- **Status**: ⚠️ Needs SQLite integration

### 4. SQLite Initialization
- **File**: `backend/app/db/init_sqlite.py` (60 lines)
- **Features**: Creates games table with full schema
- **Schema**: id, slug, title, description, rules/setup/gameplay summaries, bgg_id, URLs, metadata, timestamps
- **Status**: ✅ Ready for use

### 5. FastAPI Main App
- **File**: `backend/app/main.py` (48 lines)
- **⚠️ Issues**:
  - Still imports v1 components (ValidationMiddleware, seo_renderer, sitemap)
  - Imports non-existent routers
  - Needs cleanup for v2
- **Status**: ⚠️ Needs cleanup

## Pending Components

### 1. SQLite Integration (BGG Service)
- Update `bgg_service.py` to use SQLite instead of Supabase
- Create `backend/app/core/sqlite_client.py` wrapper

### 2. NotebookLM Pipeline
- Integrate NotebookLM CLI for slide/video/summary generation
- Implement `backend/app/services/notebooklm_pipeline.py`

### 3. FastAPI Cleanup & Routers
- Remove v1 dependencies from main.py
- Create `backend/app/routers/games.py` with endpoints:
  - GET /games - list all
  - POST /games/sync-bgg - fetch from BGG
  - GET /games/{slug} - detail view

### 4. Frontend (Simple HTML/Flask)
- Create local-only UI
- Game list, sync button, preview

## Next Actions

1. **Update BGG Service to SQLite** (High Priority)
   - Create SQLite client wrapper
   - Update bgg_service.py to use it
   - Run existing tests to verify

2. **Clean up main.py** (Medium Priority)
   - Remove v1 imports
   - Keep only health check and CORS
   - Add proper router includes

3. **NotebookLM Integration** (Medium Priority)
   - Design pipeline
   - Create CLI wrapper
   - Test with sample game

4. **Frontend Setup** (Low Priority)
   - Simple HTML or Flask
   - Game list view
   - Sync trigger button
