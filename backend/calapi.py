import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DEFAULT_CALENDAR_ID = "54d33b5da85ac849627cf6d0bf1a7d09e5eb9afe42d6be24b3c5e9ade279cc35@group.calendar.google.com"


def authenticate_google_calendar():
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
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
                    "summary": event["summary"],
                    "description": event.get("description", ""),
                    "start": event["start"].get("dateTime", event["start"].get("date")),
                    "end": event["end"].get("dateTime", event["end"].get("date")),
                    "status": event["status"],
                    "link": event["htmlLink"],
                }
                extracted_events.append(extracted_event)

            all_events.extend(extracted_events)

        return all_events

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


# Example usage:
# all_events = extract_calendar_events()
# filtered_events = extract_calendar_events(start_date="2024-10-15", end_date="2024-10-20")


if __name__ == "__main__":
    all_events = extract_calendar_events()
    for event in all_events:
        print(event)
