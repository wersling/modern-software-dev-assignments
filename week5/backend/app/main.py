import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from .db import apply_seed_if_needed, engine
from .exceptions import AppException
from .models import Base
from .routers import action_items as action_items_router
from .routers import notes as notes_router
from .routers import tags as tags_router

# Configure logging
logger = logging.getLogger(__name__)

app = FastAPI(title="Modern Software Dev Starter (Week 5)")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure data dir exists
Path("data").mkdir(parents=True, exist_ok=True)

# Mount static frontend assets (only if dist exists)
frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    # Mount assets directory for JavaScript and CSS files
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    apply_seed_if_needed()


# =============================================================================
# Exception Handlers
# =============================================================================


@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException) -> JSONResponse:
    """Handle all custom AppException subclasses.

    Returns a consistent error envelope format for all application errors.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        },
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic ValidationError (422).

    This occurs when request body validation fails.
    Returns envelope format with validation details.
    """
    # Extract first validation error for user-friendly message
    errors = exc.errors()
    first_error = errors[0] if errors else {}

    # Build error message from validation error
    field_path = " -> ".join(str(loc) for loc in first_error.get("loc", []))
    message = first_error.get("msg", "Validation error")

    if field_path:
        user_message = f"{field_path}: {message}"
    else:
        user_message = message

    return JSONResponse(
        status_code=422,
        content={
            "ok": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": user_message,
            },
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPException.

    Preserves backward compatibility for endpoints still using HTTPException.
    Maps HTTP status codes to error codes.
    """
    # Map HTTP status codes to error codes
    status_code_to_error_code = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR",
    }

    error_code = status_code_to_error_code.get(exc.status_code, "INTERNAL_ERROR")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "error": {
                "code": error_code,
                "message": str(exc.detail),
            },
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions.

    This is a catch-all for unexpected errors.
    Logs the full error for debugging but returns generic message to client.
    """
    # Log the full exception for debugging
    logger.error(
        "Unhandled exception",
        exc_info=True,
        extra={"path": str(request.url), "method": request.method},
    )

    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
            },
        },
    )


# =============================================================================
# Routers
# =============================================================================

app.include_router(notes_router.router)
app.include_router(action_items_router.router)
app.include_router(tags_router.router)


@app.get("/vite.svg")
async def serve_vite_svg() -> FileResponse:
    """Serve vite.svg icon"""
    svg_path = frontend_dist / "vite.svg"
    if svg_path.exists():
        return FileResponse(str(svg_path), media_type="image/svg+xml")
    raise HTTPException(status_code=404, detail="Icon not found")


@app.get("/")
async def root() -> FileResponse:
    """Serve the React SPA"""
    index_path = frontend_dist / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Backend API is running. Frontend not built."}


# SPA fallback - all unmatched routes return index.html for client-side routing
@app.get("/{full_path:path}")
async def serve_spa(full_path: str) -> FileResponse:
    """Fallback route for SPA - returns index.html for all non-API routes"""
    # Don't intercept API routes - return 404 for unmatched API paths
    if full_path.startswith("notes/") or full_path.startswith("action-items/") or full_path.startswith("tags/"):
        raise HTTPException(status_code=404, detail="Not found")

    # For all other paths, serve the SPA (if built)
    index_path = frontend_dist / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Backend API is running. Frontend not built."}
