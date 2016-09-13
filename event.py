from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import datetime

def add_to_calendar(start, end):
    flags = None

    SCOPES = 'https://www.googleapis.com/auth/calendar'
    store = file.Storage('storage.json')
    creds = store.get()
    CAL = build('calendar', 'v3', http=creds.authorize(Http()))

    EVENT = {
        'summary': 'Time for a Workout',
        'location': 'Gym',
        'description': 'A chance to get off your lazy ass.',
        'start': {
            'dateTime': start + '-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end + '-07:00',
            'timeZone': 'America/Los_Angeles',
        },
    }

    e = CAL.events().insert(calendarId='primary',sendNotifications=True, body=EVENT).execute()
