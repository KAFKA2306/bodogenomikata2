from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

from app import routers as games
from app.core.logger import setup_logging
from app.core.sqlite_client import init_database

setup_logging()
app = FastAPI(title="bodoge-no-mikata v2", version="2.0.0")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
STATIC_DIR = PROJECT_ROOT / "static"

ASSETS_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)


class CacheControlledStaticFiles(StaticFiles):
    def file_response(self, *args, **kwargs) -> Response:
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


# Serve /assets separately for Vite build assets
app.mount("/assets", CacheControlledStaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")

# Serve fallback index.html and other static files at the root
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


@app.on_event("startup")
async def startup_event():
    init_database()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router, prefix="/api", tags=["games"])


@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
