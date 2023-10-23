import uuid
import os
import json
import mysql.connector
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# Google Calendar API Settings
SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRET_FILE = 'client_secret_crm.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
CALENDAR_ID = 'system.evo.crm@gmail.com'

def generate_unique_event_id():
    return str(uuid.uuid4())

def read_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

def get_sql_events(config):
    database_config = {
        'user': config['database']['user'],
        'password': config['database']['password'],
        'host': config['database']['host'],
        'port': config['database']['port'],
        'database': config['database']['database_name'],
        'raise_on_warnings': True
    }

    try:
        # Connect to the database
        connection = mysql.connector.connect(**database_config)

        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Example: Execute a simple query
        cursor.execute("SELECT cr.values FROM compose_record cr WHERE rel_module = '353947921997627395';")

        # Fetch and print the results
        if connection.is_connected():
            print("Connected to the database.")
            result = cursor.fetchall()
            for row in result:
                print(row)

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor and connection
        if 'cursor' in locals() and cursor is not None:
            cursor.fetchall()
            cursor.close()
        if 'connection' in locals() and connection is not None:
            connection.close()

    return result

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
    config = read_config('database_config.json')
    sql_events = get_sql_events(config)
    print(sql_events)
    
    # # Mock data for test
    # event_title = 'Meeting with SUPER VIP'
    # start_time = '2023-10-20T09:00:00'
    # end_time = '2023-10-20T18:00:00'
    # description = 'Discussing important matters'
    # guest_emails = ['suphakin.th@gmail.com', 'system.evo.crm@gmail.com']
    # create_event(service, event_title, start_time, end_time, description, guest_emails)
if __name__ == '__main__':
    main()
