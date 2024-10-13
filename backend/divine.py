import os
import logging
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any
from functools import wraps
from typing_extensions import Annotated
import aiofiles
from fastapi import FastAPI, File, UploadFile, Body, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask
from pydantic_settings import BaseSettings
import uvicorn
from asyncio import wrap_future
import json
from calapi import authenticate_google_calendar, extract_calendar_events, update_event

from ai_calendar_processor import AICalendarProcessor
from ai_enlightened_chatbot import AIEnlightenedChatBot

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Divine Calendar API", version="0.0.1")

cal_ids = []
events = []
service = None
counter = 0
last_date = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, replace with specific origins if needed
    allow_credentials=True,
    allow_methods=[
        "*"
    ],  # Allows all methods (GET, POST, etc.), replace with specific methods if needed
    allow_headers=["*"],  # Allows all headers, replace with specific headers if needed
)


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


@lru_cache(maxsize=1)
def get_chat_bot() -> AIEnlightenedChatBot:
    return AIEnlightenedChatBot()


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
    calendar_ids: list[str] = Body(...),
    date: str = Body(...),
    questionnaire: str = None,
    processor: AICalendarProcessor = Depends(get_calendar_processor),
) -> JSONResponse:
    global cal_ids, events, service, counter

    if not cal_ids or cal_ids != calendar_ids or last_date != date:
        cal_ids = calendar_ids
        events = extract_calendar_events(
            service,
            calendar_ids=calendar_ids,
            start_date=date,
            end_date=date,
        )
        counter += 1

    try:

        output = processor.predict(events, questionnaire=questionnaire)
        for event in output["events"]:
            update_event(
                service,
                calendar_id=event["calendar_id"],
                event_id=event["id"],
                values=event,
            )
        return HTMLResponse(status_code=200, content=output)

    except Exception as exc:
        pass


@app.post("/query_chat_bot")
@handle_exception
async def query_char_bot(
    query: str = Body(...),
    agent: str = Body(...),
    processor: AIEnlightenedChatBot = Depends(get_chat_bot),
) -> JSONResponse:
    if not agent in ["philosopher", "lawyer", "monk", "productivity"]:
        raise HTTPException(status_code=400, detail="Invalid agent type")

    return JSONResponse(status_code=200, content=processor.predict(query, agent=agent))


@app.get("/health")
async def health_check() -> JSONResponse:
    return JSONResponse(content={"status": "healthy"})


if __name__ == "__main__":
    get_chat_bot()
    service = authenticate_google_calendar()
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
