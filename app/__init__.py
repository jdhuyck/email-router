from fastapi import FastAPI

from app.api.endpoints import router as api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Email Router API is running."}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
