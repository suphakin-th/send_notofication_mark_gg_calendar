import uuid
import os
import pyodbc
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# # SQL Server Connection Settings
# sql_server = 'your_sql_server'
# database = 'your_database'
# username = 'your_username'
# password = 'your_password'

# conn_str = f'DRIVER={{SQL Server}};SERVER={sql_server};DATABASE={database};UID={username};PWD={password}'

# Google Calendar API Settings
SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRET_FILE = 'client_secret_crm.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
CALENDAR_ID = 'system.evo.crm@gmail.com'

def generate_unique_event_id():
    return str(uuid.uuid4())

# def get_sql_events():
#     # For local test
#     con = sqlite3.connect("events.db")
#     cur = con.cursor()
    
#     cur.execute("SELECT * FROM events_table;")
#     events = cur.fetchall()
#     cur.close()
#     con.close()

    
#     # Connect to SQL Server and fetch events
#     # connection = pyodbc.connect(conn_str)
#     # cursor = connection.cursor()

#     # cursor.execute('SELECT event_id, event_title, event_start_time, event_end_time FROM events_table')
#     # events = cursor.fetchall()
#     # print('xxx', events)
#     # cursor.close()
#     # connection.close()

#     return events

def create_event(service, event_title, start_time, end_time, description, guest_emails):
    attendees = [{'email': email} for email in guest_emails]
    event = {
        'summary': event_title,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Bangkok',  # Thailand time zone
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Bangkok',  # Thailand time zone
        },
        'attendees': attendees,
    }

    # Insert the event directly specifying the calendarId
    event = service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()

    print('Event created: %s' % (event.get('htmlLink')))
    
def main():
    # Connect to database and get data
    """
    con = sqlite3.connect("events.db")
    cur = con.cursor()

    res = cur.execute("SELECT * FROM events_table;")
    res.fetchall()
    """
    
    # Connect to Google Calendar API
    creds = None

    if os.path.exists(CLIENT_SECRET_FILE):
        creds = Credentials.from_authorized_user_file(CLIENT_SECRET_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(CLIENT_SECRET_FILE, 'w') as token:
            token.write(creds.to_json())

    service = build(API_NAME, API_VERSION, credentials=creds)

    # Get events from SQL Server
    ## sql_events = get_sql_events()
    
    # Mock data for test
    event_title = 'Meeting with SUPER VIP'
    start_time = '2023-10-20T09:00:00'
    end_time = '2023-10-20T18:00:00'
    description = 'Discussing important matters'
    guest_emails = ['suphakin.th@gmail.com', 'system.evo.crm@gmail.com']
    create_event(service, event_title, start_time, end_time, description, guest_emails)
if __name__ == '__main__':
    main()
