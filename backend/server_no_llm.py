from http.client import HTTPException
import anthropic
from fastapi import FastAPI
from pydantic import BaseModel
from calapi import (
    authenticate_google_calendar,
    extract_calendar_events,
    update_or_create_event,
)
from fastapi.middleware.cors import CORSMiddleware
import base64
import json
from fastapi.responses import JSONResponse
from fastapi import File, UploadFile
from itertools import chain
import uvicorn
import os

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

app = FastAPI()
cal_ids = []
events = []
service = None
counter = 0
date = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, replace with specific origins if needed
    allow_credentials=True,
    allow_methods=[
        "*"
    ],  # Allows all methods (GET, POST, etc.), replace with specific methods if needed
    allow_headers=["*"],  # Allows all headers, replace with specific headers if needed
)

claude_model = "claude-3-5-sonnet-20240620"  # Model name for Claude API
client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=ANTHROPIC_API_KEY
)


# Define the Pydantic model to validate the request body
class CalendarRequest(BaseModel):
    calendar_ids: list[str]
    date: str = None
    questionnaire: str


@app.post("/process_calendar_events/")
async def process_calendar_events(request: CalendarRequest):
    global cal_ids, events, service, counter, client

    if not cal_ids or cal_ids != request.calendar_ids or date != request.date:
        cal_ids = request.calendar_ids
        events = extract_calendar_events(
            service,
            calendar_ids=request.calendar_ids,
            start_date=request.date,
            end_date=request.date,
        )
        counter += 1

    str_friendly_events = [
        f"{event['summary']} from {event['start']} to {event['end']}"
        for event in events
    ]

    prompt = f"""
You are an AI assistant specialized in calendar management and scheduling. Your task is to create or update events based on the given information and constraints.

Current Calendar Events:
{', '.join(str_friendly_events)}

User's Questionnaire:
{request.questionnaire}

Instructions:
1. Analyze the current calendar events and the user's questionnaire.
2. Create new events or update existing ones to accommodate the user's requirements.
3. Output ONLY an array of JSON objects representing the events to be created or updated.
4. Do not move or modify existing events unless absolutely necessary.
5. For new events, omit the 'id' field. For updating existing events, include the 'id' field.

Event JSON Format:
{json.dumps(events[0], indent=2)}

Rules:
- Output ONLY the JSON array, with no additional text or explanations.
- Ensure all required fields are present in each event object.
- Use ISO 8601 format for date-time values (e.g., "2024-03-15T09:00:00-07:00").
- Do not schedule events outside of typical working hours (8 AM to 6 PM) unless specified.
- Allow for reasonable buffer times between events (e.g., 15-30 minutes).
- If updating an existing event is necessary, include its 'id' and modify only the required fields.

Your response should be a valid JSON array that can be directly parsed and used by the calendar API.
    """

    try:
        client_response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        response_text = client_response.content[0].text
        response_dict = json.loads(response_text)

        for event in response_dict:
            update_or_create_event(service, event_data=event)

        return response_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Read the file content
        file_content = await file.read()

        # Convert the file content to base64
        encoded_image_data = base64.b64encode(file_content).decode("utf-8")
        image_media_type = file.content_type  # Get the file's media type

        # Construct the payload for Claude API
        message = client.messages.create(
            model=claude_model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": image_media_type,
                                "data": encoded_image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Explain the following image",
                        },
                    ],
                }
            ],
        )

        raw = "".join(chain.from_iterable(msg.text for msg in message.content))

        return JSONResponse(content={"response": raw})

    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    service = authenticate_google_calendar()
    uvicorn.run(app, host="127.0.0.1", port=8000)
