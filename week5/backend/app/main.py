from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import apply_seed_if_needed, engine
from .models import Base
from .routers import action_items as action_items_router
from .routers import notes as notes_router

app = FastAPI(title="Modern Software Dev Starter (Week 5)")

# Ensure data dir exists
Path("data").mkdir(parents=True, exist_ok=True)

# Mount static frontend (serves the built React app) - only if dist exists
frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    apply_seed_if_needed()


# Routers - must be declared before the SPA fallback
app.include_router(notes_router.router)
app.include_router(action_items_router.router)


@app.get("/")
async def root() -> FileResponse:
    """Serve the React SPA"""
    index_path = frontend_dist / "index.html"
    if index_path.exists():
        return FileResponse("frontend/dist/index.html")
    return {"message": "Backend API is running. Frontend not built."}


# SPA fallback - all unmatched routes return index.html for client-side routing
@app.get("/{full_path:path}")
async def serve_spa(full_path: str) -> FileResponse:
    """Fallback route for SPA - returns index.html for all non-API routes"""
    # Don't intercept API routes - return 404 for unmatched API paths
    if full_path.startswith("notes/") or full_path.startswith("action-items/"):
        raise HTTPException(status_code=404, detail="Not found")

    # For all other paths, serve the SPA (if built)
    index_path = frontend_dist / "index.html"
    if index_path.exists():
        return FileResponse("frontend/dist/index.html")
    return {"message": "Backend API is running. Frontend not built."}
