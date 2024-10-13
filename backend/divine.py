import os
import logging
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any
from functools import wraps
from typing_extensions import Annotated
import aiofiles
from fastapi import FastAPI, File, UploadFile, Body, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask
from pydantic_settings import BaseSettings
import uvicorn
from asyncio import wrap_future
import requests
import json

from ai_calendar_processor import AICalendarProcessor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Divine Calendar API", version="0.0.1")


class Settings(BaseSettings):
    upload_folder: str = "uploads"
    allowed_extensions: set = {"jpg", "jpeg", "png", "gif"}
    max_workers: int = 4
    host: str = "0.0.0.0"
    port: int = 5001

    class Config:
        env_file = ".env"


settings = Settings()


@lru_cache(maxsize=1)
def get_calendar_processor() -> AICalendarProcessor:
    return AICalendarProcessor()


def allowed_file(filename: str) -> bool:
    """
    Check if the given filename has an allowed extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file has an allowed extension, False otherwise.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in settings.allowed_extensions
    )


def handle_exception(func: Callable) -> Callable:
    """Decorator to handle exceptions in endpoint functions."""

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except HTTPException as http_exc:
            logger.error(f"HTTP Exception: {http_exc.detail}")
            raise
        except Exception as exc:
            logger.exception("An unexpected error occurred")
            raise HTTPException(status_code=500, detail=str(exc))

    return wrapper


@app.post("/process_calendar_events")
@handle_exception
async def process_calendar(
    events: Annotated[list[dict], Body()],
    questionnaire: str = None,
    processor: AICalendarProcessor = Depends(get_calendar_processor),
) -> JSONResponse:
    try:
        output = processor.predict(events, questionnaire=questionnaire)
        return JSONResponse(content=output)
    except Exception as exc:
        pass


@app.get("/health")
async def health_check() -> JSONResponse:
    return JSONResponse(content={"status": "healthy"})


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
