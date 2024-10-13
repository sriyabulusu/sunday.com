"""
The Divine Calendar API is a FastAPI application that provides endpoints for
processing calendar events and querying a chatbot.

The application uses the `ai_calendar_processor` and `ai_enlightened_chatbot`
modules to process calendar events and query the chatbot, respectively.

The application also uses the `calapi` module to authenticate with Google
Calendar and extract events from the calendar.

The application is configured using environment variables. The
`UPLOAD_FOLDER` environment variable specifies the folder where uploaded
files are stored. The `ALLOWED_EXTENSIONS` environment variable specifies the
allowed file extensions for uploaded files. The `MAX_WORKERS` environment
variable specifies the maximum number of workers to use for processing
uploaded files.

The application has the following endpoints:

* `/process_calendar_events`: Processes a list of calendar events and
  returns the processed events.
* `/query_chat_bot`: Queries the chatbot with a given query and returns the
  response.
* `/health`: Returns a health check response.
"""

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
from calapi import (
    authenticate_google_calendar,
    extract_calendar_events,
    update_or_create_event,
)

from ai_calendar_processor import AICalendarProcessor
from ai_enlightened_chatbot import RAGAgent

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
    """
    The application settings.

    The settings are loaded from environment variables. The environment
    variables are:

    * `UPLOAD_FOLDER`: The folder where uploaded files are stored.
    * `ALLOWED_EXTENSIONS`: The allowed file extensions for uploaded files.
    * `MAX_WORKERS`: The maximum number of workers to use for processing
      uploaded files.
    """

    upload_folder: str = "uploads"
    allowed_extensions: set = {"jpg", "jpeg", "png", "gif"}
    max_workers: int = 4
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        """
        The configuration for the settings.

        The configuration is used to load the settings from environment
        variables.
        """

        env_file = ".env"


settings = Settings()


@lru_cache(maxsize=1)
def get_calendar_processor() -> AICalendarProcessor:
    """
    Returns an instance of the `AICalendarProcessor` class.

    The instance is cached using the `lru_cache` decorator.
    """
    return AICalendarProcessor()


@lru_cache(maxsize=1)
def get_chat_bot() -> RAGAgent:
    """
    Returns an instance of the `AIEnlightenedChatBot` class.

    The instance is cached using the `lru_cache` decorator.
    """
    return RAGAgent()


def allowed_file(filename: str) -> bool:
    """
    Checks if the given filename has an allowed extension.

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
    """
    A decorator to handle exceptions in endpoint functions.

    Args:
        func (Callable): The function to decorate.

    Returns:
        Callable: The decorated function.
    """

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
    questionnaire: str = Body(...),
    processor: AICalendarProcessor = Depends(get_calendar_processor),
) -> JSONResponse:
    """
    Processes a list of calendar events and returns the processed events.

    Args:
        calendar_ids (list[str]): The list of calendar IDs to process.
        date (str): The date to process events for.
        questionnaire (str): The questionnaire to use for processing events.
        processor (AICalendarProcessor): The `AICalendarProcessor` instance to use for
            processing events.

    Returns:
        JSONResponse: The processed events.
    """

    global cal_ids, events, counter

    service = authenticate_google_calendar()
    if not cal_ids or cal_ids != calendar_ids or last_date != date:
        cal_ids = calendar_ids
        events = extract_calendar_events(
            service,
            calendar_ids=calendar_ids,
            start_date=date,
            end_date=date,
        )
        counter += 1
        print(events)

    try:
        output = processor.predict(events, questionnaire=questionnaire)
        print(output)
        for event in output:
            update_or_create_event(
                service,
                event_data=event,
            )
        return HTMLResponse(status_code=200, content=output)

    except Exception as exc:
        pass


@app.post("/query_chat_bot")
@handle_exception
async def query_char_bot(
    query: str = Body(...),
    agent: str = Body(...),
    processor: RAGAgent = Depends(get_chat_bot),
) -> JSONResponse:
    """
    Queries the chatbot with a given query and returns the response.

    Args:
        query (str): The query to ask the chatbot.
        agent (str): The agent to use for querying the chatbot.
        processor (AIEnlightenedChatBot): The `AIEnlightenedChatBot` instance to use for
            querying the chatbot.

    Returns:
        JSONResponse: The response from the chatbot.
    """

    if not agent in ["philosopher", "lawyer", "monk", "productivity"]:
        raise HTTPException(status_code=400, detail="Invalid agent type")

    return JSONResponse(
        status_code=200, content=processor.query(query, agent_type=agent)
    )


@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Returns a health check response.

    Returns:
        JSONResponse: A health check response.
    """
    return JSONResponse(content={"status": "healthy"})


if __name__ == "__main__":
    # get_chat_bot()
    service = authenticate_google_calendar()
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
