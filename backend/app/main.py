"""
NeuraCity FastAPI Backend Application
Main application file with all routes, middleware, and configuration.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os

from app.core.config import get_settings
from app.api.endpoints import issues, mood, traffic, noise, routing, admin, risk_index, users, accidents, risk

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting NeuraCity API...")
    logger.info(f"Upload directory ready: {settings.UPLOAD_DIR}")

    yield

    logger.info("Shutting down NeuraCity API...")
    # Save geocoding cache before shutdown
    try:
        from app.services.geocoding_service import save_cache
        save_cache()
        logger.info("Geocoding cache saved")
    except Exception as e:
        logger.warning(f"Failed to save geocoding cache on shutdown: {e}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent, Human-Centered Smart City Platform API",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount(f"/{settings.UPLOAD_DIR}", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Optionally serve frontend static files if they exist (for Railway deployment)
# Try multiple possible paths for frontend dist
possible_paths = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist"),
    os.path.join(os.getcwd(), "frontend", "dist"),
    os.path.join(os.path.dirname(os.getcwd()), "frontend", "dist"),
]
frontend_dist = None
for path in possible_paths:
    if os.path.exists(path) and os.path.isdir(path):
        frontend_dist = path
        break

if frontend_dist:
    # Serve frontend static files (CSS, JS, images, etc.)
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="frontend-assets")
    
    # Serve other static files from dist
    app.mount("/static", StaticFiles(directory=frontend_dist), name="frontend-static")
    
    logger.info(f"Serving frontend static files from {frontend_dist}")
else:
    logger.info("Frontend dist directory not found, serving API only")


@app.get("/")
async def root():
    """Root endpoint - serves API info or frontend if available."""
    if frontend_dist:
        # If frontend exists, serve it
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            from fastapi.responses import FileResponse
            return FileResponse(index_path)
    
    # Otherwise return API info
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.VERSION}


app.include_router(issues.router, prefix=settings.API_V1_PREFIX)
app.include_router(mood.router, prefix=settings.API_V1_PREFIX)
app.include_router(traffic.router, prefix=settings.API_V1_PREFIX)
app.include_router(noise.router, prefix=settings.API_V1_PREFIX)
app.include_router(routing.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(risk_index.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(accidents.router, prefix=settings.API_V1_PREFIX)
app.include_router(risk.router, prefix=settings.API_V1_PREFIX)

logger.info(f"All routers loaded. API prefix: {settings.API_V1_PREFIX}")

# Catch-all route for SPA (must be last, after all API routes)
if frontend_dist:
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve frontend SPA for all non-API routes."""
        # Don't interfere with API routes, health, or docs
        if (full_path.startswith("api/") or 
            full_path.startswith("docs") or 
            full_path.startswith("openapi.json") or
            full_path == "health"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve index.html for SPA client-side routing
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            from fastapi.responses import FileResponse
            return FileResponse(index_path)
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Frontend not found")
