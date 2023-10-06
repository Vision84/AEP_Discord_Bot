from __future__ import print_function

import os.path
from pprint import pprint

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def oauth():
    # If modifying these scopes, delete the file token.json.
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
        return creds
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            return creds


def get_schedules():
    CREDS = oauth()

    # The ID and range of the spreadsheet.
    SPREADSHEET_ID = '191gADUNLcjJbURBXhWQ5r4v7qyecpAFVta8tZ-bCCK0'
    SHEETS = ["General Math", "General English", "General Science", "Advanced Math", "Advanced Science", "Computer Science"]

    try:
        service = build('sheets', 'v4', credentials=CREDS) 

        # Call the Sheets API
        sheet = service.spreadsheets()

        SCHEDULES = {}
        for range in SHEETS:
            result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=range).execute()
            values = result.get('values', [])

            if not values:
                print('No data found.')
                return

            # convert [[], []] to [{}, {}]
            # The first row are the keys
            keys = values[0]
            schedule = []
            for row in values[1:]:
                d = {k:v for k, v in zip(keys, row)}
                schedule.append(d)

            SCHEDULES[range] = schedule
        
    except HttpError as err:
        print(err)
    
    return SCHEDULES


def get_hours(name):
    CREDS = oauth()
    try: 
        service = build('sheets', 'v4', credentials=CREDS) 

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId="1B67ypKapKiNxrbph0144ngHqt-FRRHyh-BDax7rqIMo", range="Hours!A2:B50").execute()
        values = result.get('values', [])

        if not values:
            return None

        for value in values:
            if name == value[0].lower().strip():
                return value[1].strip()

    except HttpError as err:
        print(err)
        return None


def get_top_volunteers(top):
    CREDS = oauth()
    try: 
        service = build('sheets', 'v4', credentials=CREDS) 

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId="1B67ypKapKiNxrbph0144ngHqt-FRRHyh-BDax7rqIMo", range="Hours!A2:B50").execute()
        values = result.get('values', [])

        if not values:
            return None

        values.sort(key=lambda x:float(x[1]), reverse=True)
        return values[:top]


    except HttpError as err:
        print(err)
        return None


# Testing functions
if __name__ == '__main__':
    pprint(get_schedules())