import os

import pyodbc
import sqlite3
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
CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
CALENDAR_ID = 'suphakin.th@gmail.com'

def get_sql_events():
    # For local test
    con = sqlite3.connect("events.db")
    cur = con.cursor()
    
    cur.execute("SELECT * FROM events_table;")
    events = cur.fetchall()
    cur.close()
    con.close()

    
    # Connect to SQL Server and fetch events
    # connection = pyodbc.connect(conn_str)
    # cursor = connection.cursor()

    # cursor.execute('SELECT event_id, event_title, event_start_time, event_end_time FROM events_table')
    # events = cursor.fetchall()
    # print('xxx', events)
    # cursor.close()
    # connection.close()

    return events

def create_google_event(service, summary, start_time, end_time):
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'UTC'},
        'end': {'dateTime': end_time, 'timeZone': 'UTC'},
    }

    service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

def main():
    con = sqlite3.connect("events.db")
    cur = con.cursor()

    res = cur.execute("SELECT * FROM events_table;")
    res.fetchall()
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
    sql_events = get_sql_events()

    # Create corresponding events in Google Calendar
    for event_id, event_title, start_time, end_time in sql_events:
        create_google_event(service, event_title, start_time, end_time)
        print(f'Event {event_id} created in Google Calendar.')

if __name__ == '__main__':
    main()
