import os
import random
import sys
import schedule
import time
import json
import numbers
import decimal
import sqlite3
import threading
from slackclient import SlackClient

import person
import util
import workout
import scheduler

"""
Complete:
    - connect this to data base:
        http://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html
Notes:
    - to run bot, follow these commands:
        https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
    - make each person an object, follow this guide
        https://jeffknupp.com/blog/2014/06/18/improve-your-python-python-classes-and-object-oriented-programming/
Later:
    - how to upload images from local computer using slack API?
    - add image for each workout? track each excercise?
    - run summary reports from data base on command
    - incorporate Google Calendar API to add workout events to your calendar [do i have a user's email?]
"""

# starterbot's ID as an environment variable
BOT_ID = os.environ.get('BOT_ID')
AT_BOT = "<@" + str(BOT_ID) + ">:"

# starter commands
HELLO_COMMAND   = ["hello", "morning"]
SUMMARY_COMMAND = ["summary", "report"]
WORKOUT_LIST    = {'2-knee-up-crunches.gif': 'knee up crunches',
                   '1-standard-crunch.gif': 'standard crunches'}
                    # '3-hip-lifts.gif': ,
                    # '4-oblique-crunches.gif': ,
                    # '5-side-plank-dips.gif': ,
                    # '6-oblique-leg-extensions.gif': ,
                    # '7-supermans.gif': ,
                    # '8-bridged-plank-leg-lifts.gif': ,
                    # '9-pushup.gif': ,
                    # '10-heel-touches.gif': ,
                    # '11-bicycle.gif': ,
                    # '12-half-up-twists.gif': }

ACTIVE_USERS = ['stephen'] #, 'ecprokop']

# instantiate Slack & Twilio clients
SLACK_MAIN = SlackClient(os.environ.get('SLACK_TOKEN'))

def handle_command(command, person, job_status):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    # time to set schedule on Sundays
    hour = 20; error_message = True

    if person.status == 'active' and person.name in ACTIVE_USERS:
        workout.during(person)
    elif command == 'summary' and person.name in ACTIVE_USERS:
        person.summary_report()
    elif not person.routine and person.name in ACTIVE_USERS:
        time_str = str(hour) + ':00'
        message = 'hey @' + person.name + ', it looks like you don\'t a schedule set up yet. we\'ll do that for you ' \
            + 'on *sunday* at *' + person.get_local_time(time_str) + '*.'
        person.client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
        # person.my_schedule.schedule.every().sunday.at(time_str).do(set_routine, person, schedule)
        person.my_schedule.schedule.every(1).minutes.do(set_routine, person)
        job_status = True
    else:
        message = 'we\'re still building out our functionality. come back in a few weeks.'
        person.client.api_call('chat.postMessage', channel=person.channel, text=message, as_user=True)
    return job_status

def set_routine(person):
    print '[main.set_routine()]: setting routine for ' + person.name

    message = 'we are going to set up your schedule for the week now. please provide workout times in 24-hour format (i.e. 6:30 or 13:10). if you do not want to work out that day, say *no*.'
    person.client.api_call('chat.postMessage', channel=person.channel, text=message, as_user=True)
    message = ''
    for i in util.days_of_week:
        message += 'what time do you want to workout on ' + i + '?'
        person.client.api_call('chat.postMessage', channel=person.channel, text=message, as_user=True)
        start_time = None

        while start_time == None:
            start_time, channel, user_name = util.parse_slack_output(person.client.rtm_read(), person.client)
            time.sleep(READ_WEBSOCKET_DELAY)

        if start_time == 'no':
            message = 'okay, I won\'t bother you on ' + i + '. '
            continue
        message = ''
        hour = int(start_time.split(":")[0]) - util.gmt_x_timezone[person.timezone]
        minute = start_time.split(":")[1]
        start_time = str(hour) + ":" + str(minute)
        person.set_routine(start_time, i)

    message = 'great, your schedule is all set.'
    person.client.api_call('chat.postMessage', channel=person.channel, text=message, as_user=True)
    person.my_schedule.start_persons_workout(person)
    return schedule.CancelJob

def start_bot_activity(ids_x_person, p):
    print '[main.start_bot_activity()]: starting bot activity for ' + p

    person_id = ''
    for temp_id, temp_person in ids_x_person.iteritems():
        if temp_person.name == p:
            person_id = temp_id

    if ids_x_person[person_id].client.rtm_connect():
        jobs_scheduled = False
        while True:
            ''' need to send start of workout message here '''

            try:
                command, channel, user_id = util.parse_slack_output(ids_x_person[person_id].client.rtm_read(), ids_x_person[person_id].client)
            except Exception as e:
                print '--- error: ' + e + ' ---'
                ids_x_person[person_id].client = SlackClient(os.environ.get('SLACK_TOKEN'))
                message = 'error: ' + str(e) + '. re-connecting gym-buddy'
                ids_x_person[person_id].client.api_call('chat.postMessage', channel=util.TESTING_CHANNEL, text=message, as_user=True)

            if command and channel == ids_x_person[person_id].channel:
                jobs_scheduled = handle_command(command, ids_x_person[person_id], jobs_scheduled)
            if jobs_scheduled:
                ids_x_person[person_id].my_schedule.run_pending()
            time.sleep(READ_WEBSOCKET_DELAY)

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1           # 1 second delay between reading from firehose
    sqlite_path = os.getcwd() + '/'    # name of the sqlite database file

    if len(sys.argv) < 2:
        print('Usage:')
        print('\tpython {} <database name>'.format(sys.argv[0]))
        exit()

    sqlite_file = sqlite_path + sys.argv[1]
    CONNECTION  = sqlite3.connect(sqlite_file, check_same_thread=False)
    DATABASE    = CONNECTION.cursor()

    workout = workout.Workout(sqlite_file)

    if SLACK_MAIN.rtm_connect():
        print('\n--- gym-buddy connected and running! ---\n')
        ids_x_person = util.get_list_of_users(SLACK_MAIN)
        bot_channels, _ = util.get_list_of_channels(SLACK_MAIN)

        # create each Person
        for i in ids_x_person:
            if i in [BOT_ID, 'USLACKBOT']:
                temp = person.Person(i, ids_x_person[i][0], ids_x_person[i][1].lower(), 'n/a', CONNECTION)
            else:
                temp = person.Person(i, ids_x_person[i][0], ids_x_person[i][1].lower(), bot_channels[i], CONNECTION)
            ids_x_person[i] = temp

        # TODO the next step is to turn this into threaded functions are all active users
        # TODO great explanation (https://pymotw.com/2/threading/)

        start_bot_activity(ids_x_person, ACTIVE_USERS[0])
        #threads = []
        #for p in range(len(ACTIVE_USERS)):
        #    t = threading.Thread(target = start_bot_activity, args=(ids_x_person, ACTIVE_USERS[p], ))
        #    threads.append(t)
        #    t.start()

    else:
        print 'Connection failed. Invalid Slack token or bot ID?'

    CONNECTION.commit()
    CONNECTION.close()
