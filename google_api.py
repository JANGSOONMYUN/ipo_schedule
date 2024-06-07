import datetime
import os.path
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def load_config():
    """Load configuration from a JSON file."""
    with open('config.json') as config_file:
        config = json.load(config_file)
    return config

def main():
    """Shows basic usage of the Google Calendar API.
    Modifies a Google Calendar event.
    """
    config = load_config()

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(config['token_file']):
        creds = Credentials.from_authorized_user_file(config['token_file'], SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config['client_secret_file'], SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(config['token_file'], 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    calendar_id = config['calendar_id']
    event_id = config['event_id']
    
    # Fetch the event
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    
    # Modify the event
    event['summary'] = 'Updated Event Summary'
    event['description'] = 'Updated Event Description'
    event['start'] = {
        'dateTime': '2023-12-25T09:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    }
    event['end'] = {
        'dateTime': '2023-12-25T17:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    }

    updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()

    print('Event updated: %s' % (updated_event.get('htmlLink')))

if __name__ == '__main__':
    main()
