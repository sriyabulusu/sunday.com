import datetime
import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DEFAULT_CALENDAR_ID = "54d33b5da85ac849627cf6d0bf1a7d09e5eb9afe42d6be24b3c5e9ade279cc35@group.calendar.google.com"
SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.events"]

def authenticate_google_calendar():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("calendar", "v3", credentials=creds)


def extract_calendar_events(
    calendar_ids=[DEFAULT_CALENDAR_ID], start_date=None, end_date=None
) -> list:

    try:
        service = authenticate_google_calendar()
        time_min = (
            f"{start_date}T00:00:00Z"
            if start_date
            else datetime.datetime.now().isoformat() + "Z"
        )
        time_max = f"{end_date}T23:59:59Z" if end_date else None

        all_events = []

        for cid in calendar_ids:
            events_result = (
                service.events()
                .list(
                    calendarId=cid,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])

            extracted_events = []
            for event in events:

                extracted_event = {
                    "id": event["id"],
                    "calendar_id": cid,
                    "calendar_name": event["organizer"].get("displayName", "Unknown"),
                    "summary": event["summary"],
                    "description": event.get("description", ""),
                    "start": event["start"].get("dateTime", event["start"].get("date")),
                    "end": event["end"].get("dateTime", event["end"].get("date")),
                    "status": event["status"],
                }

                extracted_events.append(extracted_event)

            all_events.extend(extracted_events)

        return all_events

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def update_event(service, calendar_id='primary', event_id=None, values={}):
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

    for key, value in values.items():
        event[key] = value

    updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()


if __name__ == "__main__":

    my_real_calendars = [DEFAULT_CALENDAR_ID]
    service = authenticate_google_calendar()

    for event in extract_calendar_events(calendar_ids=my_real_calendars):
        event_id = event["id"]
        cal_id = event["calendar_id"]
        print(json.dumps(event, indent=4))

        update_event(service, calendar_id=cal_id, event_id=event_id, values={"summary": "CS 42 Class"})
