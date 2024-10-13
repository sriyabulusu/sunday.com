import anthropic
from fastapi import FastAPI
from pydantic import BaseModel
from calapi import authenticate_google_calendar, extract_calendar_events
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
    allow_methods=["*"],   # Allows all methods (GET, POST, etc.), replace with specific methods if needed
    allow_headers=["*"],   # Allows all headers, replace with specific headers if needed
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
    time_wake: str = None
    time_sleep: str = None
    most_productive: str = None
    todo: str = None
@app.post("/prompt/")
def get_calendars(request: CalendarRequest):
    global cal_ids, events, service, counter

    metadata = {
        "date": request.date,
        "time_wake": request.time_wake,
        "time_sleep": request.time_sleep,
        "most_productive": request.most_productive,
        "todo": request.todo,
    }


    if not cal_ids or cal_ids != request.calendar_ids or date != request.date:
        cal_ids = request.calendar_ids
        events = extract_calendar_events(
          service,
          calendar_ids=request.calendar_ids,
          start_date=request.date,
          end_date=request.date
        )
        counter += 1

    prompt = f"""
    Here are some things you need to know about me:
    - I wake up at {metadata["time_wake"]} and sleep at {metadata["time_sleep"]}.
    - I am most productive during {metadata["most_productive"]}.
    - I want to accomplish the following on {metadata["date"]}: {metadata["todo"]}.
    """

    return


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
                        }
                    ],
                }
            ],
        )


        raw = "".join(
            chain.from_iterable(
                msg.text for msg in message.content
            )
        )

        return JSONResponse(content={"response": raw})

    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    service = authenticate_google_calendar()
    uvicorn.run(app, host="127.0.0.1", port=8000)
