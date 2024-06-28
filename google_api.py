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

def get_upcoming_events(calendar_id, max_results=50):
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
    # print(json.dumps(event, indent=4))
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

def get_calendar_id():
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
    return ipo_calendar_id
'''
{
    "kind": "calendar#event",
    "etag": "\"3437168823652000\"",
    "id": "39bsvq2053aco00t7b07mq56kb",
    "status": "confirmed",
    "htmlLink": "https://www.google.com/calendar/event?eid=Mzlic3ZxMjA1M2FjbzAwdDdiMDdtcTU2a2IgNDdlODIwN2U3Y2VkZjZhNzc4ZjljYjYzYjFmODMwMDllYTI4Njk0OWEyYmVlYzNlNWRmMWM5NjcxNTMzNmU1M0Bn",
    "created": "2024-06-17T00:33:31.000Z",
    "updated": "2024-06-17T00:33:31.826Z",
    "summary": "(\uc0c1\uc7a5) \ud558\uc774\uc820\uc54c\uc564\uc5e0 - \ud55c\ud22c",
    "creator": {
        "email": "jsm890803.3@gmail.com"
    },
    "organizer": {
        "email": "47e8207e7cedf6a778f9cb63b1f83009ea286949a2beec3e5df1c96715336e53@group.calendar.google.com",
        "displayName": "\uacf5\ubaa8\uc8fc",
        "self": true
    },
    "start": {
        "dateTime": "2024-06-27T09:00:00+09:00",
        "timeZone": "Asia/Seoul"
    },
    "end": {
        "dateTime": "2024-06-27T10:00:00+09:00",
        "timeZone": "Asia/Seoul"
    },
    "iCalUID": "39bsvq2053aco00t7b07mq56kb@google.com",
    "sequence": 0,
    "reminders": {
        "useDefault": true
    },
    "eventType": "default"
}

'''
if __name__ == '__main__':
    ipo_calendar_id = get_calendar_id()
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