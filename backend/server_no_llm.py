from fastapi import FastAPI
from pydantic import BaseModel
from calapi import authenticate_google_calendar, extract_calendar_events
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

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

    return {"events": events, "counter": counter}

if __name__ == "__main__":
    service = authenticate_google_calendar()
    uvicorn.run(app, host="127.0.0.1", port=8000)
