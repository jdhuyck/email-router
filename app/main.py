from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app.api.endpoints import router as api_router
from app.core.config import get_settings
from app.services.email_processor import email_processor

settings = get_settings()


async def email_polling_task():
    """Background task to periodically check for new emails."""
    while True:
        try:
            await email_processor.process_new_emails()
        except Exception as e:
            print(f"Error in email polling task: {e}")
        await asyncio.sleep(settings.gmail_poll_interval)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa:D103
    # Startup: Start background task
    polling_task = asyncio.create_task(email_polling_task())
    yield
    # Shutdown: Cancel background task
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/")
async def root():  # noqa:D103
    return {"message": "Email Router API is running."}


@app.get("/health")
async def health_check():  # noqa:D103
    return {"status": "healthy"}
