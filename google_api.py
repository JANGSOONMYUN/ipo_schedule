# import datetime
# import pytz
# import os.path
# import json
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

# # If modifying these SCOPES, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/calendar']
# # SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


# def load_config(file_path='config.json'):
#     """Load configuration from a JSON file."""
#     with open(file_path) as config_file:
#         config = json.load(config_file)
#     return config


# def get_calendar_service():
#     """Shows basic usage of the Google Calendar API.
#     Prints the start and name of the next 10 events on the user's calendar.
#     """
#     creds = None
#     # The file token.json stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists("token.json"):
#         creds = Credentials.from_authorized_user_file("token.json", SCOPES)
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 "credentials.json", SCOPES
#             )
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         with open("token.json", "w") as token:
#             token.write(creds.to_json())

#     try:
#         service = build("calendar", "v3", credentials=creds)
#         return service
#     except HttpError as error:
#         print(f"An error occurred: {error}")
#     return None

# def test():
#     try:
#         service = get_calendar_service()

#         # Call the Calendar API
#         now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
#         print("Getting the upcoming 10 events")
#         events_result = (
#             service.events()
#             .list(
#                 calendarId="primary",
#                 timeMin=now,
#                 maxResults=10,
#                 singleEvents=True,
#                 orderBy="startTime",
#             )
#             .execute()
#         )
#         events = events_result.get("items", [])

#         if not events:
#             print("No upcoming events found.")
#             return

#         # Prints the start and name of the next 10 events
#         for event in events:
#             start = event["start"].get("dateTime", event["start"].get("date"))
#             print(start, event["summary"])

#     except HttpError as error:
#         print(f"An error occurred: {error}")
        
# def get_upcoming_events(calendar_id, max_results=10):
#     service = get_calendar_service()
#     seoul_tz = pytz.timezone('Asia/Seoul')
#     now = datetime.datetime.now(seoul_tz).isoformat()
#     # now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
#     events_result = service.events().list(calendarId=calendar_id).execute()
#     events_result = service.events().list(calendarId=calendar_id, timeMin=now,
#                                           maxResults=max_results, singleEvents=True,
#                                           orderBy='startTime').execute()
#     events = events_result.get('items', [])

#     if not events:
#         print('No upcoming events found.')
#         return []

#     # Prepare the data for JSON
#     event_data = []
#     for event in events:
#         start = event['start'].get('dateTime', event['start'].get('date'))
#         event_info = {
#             'summary': event.get('summary', 'No title'),
#             'start': start,
#             'description': event.get('description', ''),
#             'location': event.get('location', '')
#         }
#         event_data.append(event_info)

#     # Write the data to a JSON file
#     with open('upcoming_events.json', 'w') as json_file:
#         json.dump(event_data, json_file, indent=4)

#     print('Upcoming events data written to upcoming_events.json')
#     return event_data

# def get_specific_calendar(calendar_id):
#     service = get_calendar_service()
#     calendar = service.calendars().get(calendarId=calendar_id).execute()
#     return calendar

# def list_calendars():
#     service = get_calendar_service()
#     calendar_list = service.calendarList().list().execute()

#     calendars = calendar_list.get('items', [])

#     if not calendars:
#         print('No calendars found.')
#     for calendar in calendars:
#         # print(calendar)
#         print(f"Calendar Summary: {calendar['summary']}")
#         print(f"Calendar ID: {calendar['id']}")
#         print()
#     return calendars

# # example
# def set_a_schedule(google_calendar, schedule_list: list):
#     # google_calendar = GoogleCalendar()

#     for schedule in schedule_list:
#         date = datetime.date(year=2022, month=schedule["month"], day=schedule["day"]).isoformat()
#         event = {
#             "summary": schedule["team"],  # 일정 제목
#             "location": schedule["stadium"],  # 일정 장소
#             "description": '야구 경기',  # 일정 설명
#             "start": {  # 시작 날짜
#                 "dateTime": date + f"T{schedule['begin_time']}:00",
#                 "timeZone": "Asia/Seoul",
#             },
#             "end": {  # 종료 날짜
#                 "dateTime": date + f"T{schedule['end_time']}:59",
#                 "timeZone": "Asia/Seoul",
#             },
#         }

#         google_calendar.set_google_calendar(event)

# if __name__ == "__main__":
#     # test()
    
#     # get_specific_calendar()
#     calendars = list_calendars()
    
#     ipo_calendar_id = ''
#     for c in calendars:
#         if '공모주' in c['summary']:
#             ipo_calendar_id = c['id']
#     # Write the data to a JSON file
#     with open('ipo_calendar.json', 'w') as json_file:
#         json.dump({'id': ipo_calendar_id, 'name': '공모주'}, json_file, indent=4)
            
#     ipo_calendar = get_specific_calendar(ipo_calendar_id)
#     print('ipo_calendar_id:', ipo_calendar_id)
#     print(ipo_calendar)
    
#     get_upcoming_events(ipo_calendar)
    
import datetime
import os.path
import json
import pytz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    creds = None
    
    # When google.auth.exceptions.RefreshError: ('invalid_scope: Bad Request' ...) token should be regenerated. To make sure, comment 
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    return service

def list_calendars():
    service = get_calendar_service()
    calendar_list = service.calendarList().list().execute()

    calendars = calendar_list.get('items', [])

    if not calendars:
        print('No calendars found.')
        return None

    for calendar in calendars:
        print(f"Calendar Summary: {calendar['summary']}")
        print(f"Calendar ID: {calendar['id']}")
        print()

    return calendars

def get_upcoming_events(calendar_id, max_results=20):
    service = get_calendar_service()
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.datetime.now(seoul_tz).isoformat()
    events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                          maxResults=max_results, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return []

    # Prepare the data for JSON
    event_data = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_info = {
            'id': event['id'],
            'summary': event.get('summary', 'No title'),
            'start': start,
            'description': event.get('description', ''),
            'location': event.get('location', '')
        }
        event_data.append(event_info)

    # # Write the data to a JSON file
    # with open('upcoming_events.json', 'w') as json_file:
    #     json.dump(event_data, json_file, ensure_ascii=False, indent=4)

    # print('Upcoming events data written to upcoming_events.json')
    return event_data

def get_event_details(calendar_id, event_id):
    service = get_calendar_service()
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    print(json.dumps(event, indent=4))
    return event

def add_event(calendar_id, event_details):
    service = get_calendar_service()
    event = service.events().insert(calendarId=calendar_id, body=event_details).execute()
    print(f"Event created: {event.get('htmlLink')}")
    return event

def update_event(calendar_id, event_id, updated_details):
    service = get_calendar_service()
    event = service.events().patch(calendarId=calendar_id, eventId=event_id, body=updated_details).execute()
    print(f"Event updated: {event.get('htmlLink')}")
    return event

def delete_event(calendar_id, event_id):
    service = get_calendar_service()
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    print(f"Event with ID {event_id} deleted.")
    return

def get_ipo_list():
    # get ipo list
    # 1. name
    # 2. host_company
    # 3. ipo_date
    # 4. go_public_date
    # 
    ipo_list = []
    return ipo_list


if __name__ == '__main__':
    ipo_calendar_id = ''
    if os.path.exists('ipo_calendar.json'):
        with open('ipo_calendar.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            ipo_calendar_id = data['id']
    else:
        calendars = list_calendars()
        for c in calendars:
            if '공모주' in c['summary']:
                ipo_calendar_id = c['id']
                with open('ipo_calendar.json', 'w') as json_file:
                    json.dump({'id': ipo_calendar_id, 'name': '공모주'}, json_file, indent=4)
                # # Example: Selecting the first calendar ID from the list
                # selected_calendar_id = c['id']
                # print(selected_calendar_id)
                # print(f"Selected Calendar ID: {selected_calendar_id}")
                # get_upcoming_events(selected_calendar_id)
                
                break
    # Example: Selecting the first calendar ID from the list
    print(f"Selected Calendar ID: {ipo_calendar_id}")
    events = get_upcoming_events(ipo_calendar_id)
    # print(events)
    
    if events:
        # Example: Get details of the first upcoming event
        event_id = events[0]['id']
        detail = get_event_details(ipo_calendar_id, event_id)
        print(json.dumps(detail, ensure_ascii=False, indent=4))
        
        
    ipo_list = get_ipo_list()
        
    for e in events:
        event_id = e['id']
        detail = get_event_details(ipo_calendar_id, event_id)
        
        for ipo in ipo_list:
            if ipo['name'] in detail['summary']:
                if ipo['ipo_date'] == detail['start']['dateTime']:
                    pass 