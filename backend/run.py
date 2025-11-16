"""Simple script to run the NeuraCity backend server."""
import uvicorn
import os
from app.core.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    # Railway provides PORT environment variable
    port = int(os.environ.get("PORT", settings.BACKEND_PORT))
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=port,
        reload=settings.DEBUG,
        log_level="info"
    )
