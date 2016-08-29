import os
import random
import sys
import schedule
import time
import json
import numbers
import decimal
import sqlite3
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
TODO: should person have an instance of workout class? would make things a bit 'cleaner'?
TODO: ask person what workout they are doing (run or workout)
TODO: create rest of DAG for workout routine (maybe make a workout_functions.py file)
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

ACTIVE_USERS = ['stephen']

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))

def handle_command(command, person, job_status, weekly_schedule):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    # time to set schedule on Sundays
    hour = 20; error_message = True

    if person.status == 'active' and person.name in ACTIVE_USERS:
        workout.during(person, slack_client)
    elif command == 'summary' and person.name in ACTIVE_USERS:
        message = person.summary_report()
        slack_client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
    elif not person.routine and person.name in ACTIVE_USERS:
        time_str = str(hour) + ':00'
        message = 'hey @' + person.name + ', it looks like you don\'t a schedule set up yet. we\'ll do that for you ' \
            + 'on *sunday* at *' + person.get_local_time(time_str) + '*.'
        slack_client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
        # weekly_schedule.schedule.every().sunday.at(time_str).do(set_routine, person, schedule)
        weekly_schedule.schedule.every(1).minutes.do(set_routine, person, weekly_schedule)
        job_status = True
    else:
        message = 'we\'re still building out our functionality. come back in a few weeks.'
        slack_client.api_call('chat.postMessage', channel=person.channel, text=message, as_user=True)
    return job_status

def set_routine(person, weekly_schedule):
    # print "we will ask " + person.name + " for his schedule in channel " + person.channel
    message = 'we are going to set up your schedule for the week now. please provide workout times in 24-hour format (i.e. 6:30 or 13:10). if you do not want to work out that day, say *no*.'
    slack_client.api_call('chat.postMessage', channel=person.channel, text=message, as_user=True)
    message = ''
    for i in util.days_of_week:
        message += 'what time do you want to workout on ' + i + '?'
        slack_client.api_call('chat.postMessage', channel=person.channel, text=message, as_user=True)
        start_time = None

        while start_time == None:
            start_time, channel, user_name = util.parse_slack_output(slack_client.rtm_read(), slack_client)
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
    slack_client.api_call('chat.postMessage', channel=person.channel, text=message, as_user=True)
    weekly_schedule.start_persons_workout(person)
    return schedule.CancelJob

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1           # 1 second delay between reading from firehose
    sqlite_path = os.getcwd() + '/'    # name of the sqlite database file

    if len(sys.argv) < 2:
        print('Usage:')
        print('\tpython {} <database name>'.format(sys.argv[0]))
        exit()

    sqlite_file = sqlite_path + sys.argv[1]
    CONNECTION  = sqlite3.connect(sqlite_file)
    DATABASE    = CONNECTION.cursor()

    weekly_schedule = scheduler.Scheduler()
    workout = workout.Workout(sqlite_file)

    if slack_client.rtm_connect():
        print('\n--- gym-buddy connected and running! ---\n')
        ids_x_person = util.get_list_of_users(slack_client)
        bot_channels, _ = util.get_list_of_channels(slack_client)

        # create each Person
        for i in ids_x_person:
            if i in [BOT_ID, 'USLACKBOT']:
                temp = person.Person(i, ids_x_person[i][0], ids_x_person[i][1].lower(), 'n/a', sqlite_file)
            else:
                temp = person.Person(i, ids_x_person[i][0], ids_x_person[i][1].lower(), bot_channels[i], sqlite_file)
            ids_x_person[i] = temp

        jobs_scheduled = False
        while True:
            ''' need to send start of workout message here '''
            # TODO: don't look through all people, only loop through active users
            for i in ids_x_person:
                if ids_x_person[i].status == 'start' and ids_x_person[i].name in ACTIVE_USERS:
                    workout.begin(ids_x_person[i], weekly_schedule, slack_client)
                elif ids_x_person[i].status == 'complete' and ids_x_person[i].name in ACTIVE_USERS:
                    workout.end(ids_x_person[i], slack_client)
            try:
                command, channel, user_id = util.parse_slack_output(slack_client.rtm_read(), slack_client)
            except Exception as e:
                print '--- error: ' + e + ' ---'
                slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))
                message = 'error: ' + str(e) + '. re-connecting gym-buddy'
                slack_client.api_call('chat.postMessage', channel=util.TESTING_CHANNEL, text=message, as_user=True)

            if command and channel:
                jobs_scheduled = handle_command(command, ids_x_person[user_id], jobs_scheduled, weekly_schedule)
            if jobs_scheduled:
                weekly_schedule.run_pending()
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print 'Connection failed. Invalid Slack token or bot ID?'

    CONNECTION.commit()
    CONNECTION.close()
