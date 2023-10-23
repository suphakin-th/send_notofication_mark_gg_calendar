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

def update_events(config: dict, event_id: str, link: str):
    result = None
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
        cursor.execute(f"UPDATE compose_record SET (is_gg_marked, gg_link) = (TRUE, {link}) WHERE id = {event_id}, rel_module = '353947921997627395' AND is_gg_marked = FALSE;")

        # Fetch and print the results
        result = cursor.fetchall()
        for row in result:
            print(row)
        
        if connection.is_connected() and result:
            print("Connected to the database.")
            return result


    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor and connection
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'connection' in locals() and connection is not None:
            connection.close()
    return result

def get_sql_events(config):
    result = None
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
        cursor.execute("SELECT cr.id, cr.values FROM compose_record cr WHERE rel_module = '353947921997627395' AND is_gg_marked = FALSE;")

        # Fetch and print the results
        result = cursor.fetchall()
        for row in result:
            print(row)
        
        if connection.is_connected() and result:
            print("Connected to the database.")
            return result


    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor and connection
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'connection' in locals() and connection is not None:
            connection.close()
    return result

def create_event(service, event_title, start_time, end_time, description, guest_emails, location):
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
        'location' : location
    }

    # Insert the event directly specifying the calendarId
    event = service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()

    return event.get('htmlLink')
    
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
    if sql_events and isinstance(sql_events, list) and len(sql_events )>=1 :
        # Event from database
        for event in sql_events:
            link = None
            event_id = str(event[0]).strip()
            event_data = json.loads(event[1])
            # filter only event that have ActivityDate and EndDateTime
            if event_data['ActivityDate'] and event_data['EndDateTime']:
                print('RECORD_EVENT : ', event_data)
                link = create_event(
                    service = service, 
                    event_title = 'AUTO_EVENT : ' + event_data['Subject'] if event_data['Subject'] else 'AUTO_EVENT : NO SUBJECT', 
                    start_time = event_data['ActivityDate'],
                    end_time = event_data['EndDateTime'],
                    description = event_data['Description'],
                    guest_emails = event_data['ContactId'],
                    location = event_data['Location']
                )
            else:
                continue
            # Update SQL
            if link:
                status = update_events(config=config, event_id=event_id, link=link)
                print(f'Event ID {event_id}, UPDATED') if status else print(f'Event ID {event_id}, Something wrong.')
    else:
        print("Get no data from connection")
    
    # # Mock data for test
    # event_title = 'Meeting with SUPER VIP'
    # start_time = '2023-10-20T09:00:00'
    # end_time = '2023-10-20T18:00:00'
    # description = 'Discussing important matters'
    # guest_emails = ['suphakin.th@gmail.com', 'system.evo.crm@gmail.com']
    # create_event(service, event_title, start_time, end_time, description, guest_emails)
if __name__ == '__main__':
    main()
