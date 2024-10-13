from fastapi import FastAPI
from pydantic import BaseModel
from calapi import authenticate_google_calendar, extract_calendar_events
import uvicorn

app = FastAPI()
cal_ids = []
events = []
service = None
counter = 0

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

    print(metadata)

    if not cal_ids or cal_ids != request.calendar_ids:
        cal_ids = request.calendar_ids
        events = extract_calendar_events(service, calendar_ids=request.calendar_ids)
        counter += 1

    return {"events": events, "counter": counter}

if __name__ == "__main__":
    service = authenticate_google_calendar()
    uvicorn.run(app, host="127.0.0.1", port=8000)
