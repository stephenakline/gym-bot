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
TODO: do so by having a list [possibly in scheduler] of starting, active and complete users for main.py to check,
        so we don't have to loop through all users to check
TODO: add SQL data base in main.py for workout (right now running)
TODO: ask person what workout they are doing (run or workout)
TODO: create rest of DAG for workout routine (maybe make a workout_functions.py file)
Later:
    - how to upload images from local computer using slack API?
    - add image for each workout? track each excercise?
    - run summary reports from data base on command
    - make it so bot asks me every morning at 8 am (like howdy)
    - should only say 'good morning. what did you do today?' once per day
    - do everything for 'row'
    - incorporate texting?
        - https://www.twilio.com/blog/2016/05/build-sms-slack-bot-python.html
"""

# starterbot's ID as an environment variable
# BOT_ID = os.environ.get("BOT_ID")
BOT_ID = os.environ.get('BOT_ID')

# constants
AT_BOT = "<@" + str(BOT_ID) + ">:"

# starter commands
HELLO_COMMAND   = ["hello", "morning"]
RUN_COMMAND     = ["run", "ran", "treadmill"]
ROW_COMMAND     = ["row"]
WORKOUT_COMMAND = ["workout"]
SUMMARY_COMMAND = ["summary", "report"]
WORKOUT_LIST    = {'2-knee-up-crunches.gif': 'knee up crunches',
                   '1-standard-crunch.gif': 'standard crunches'}
                    #, '3-hip-lifts.gif',
                    # '4-oblique-crunches.gif', '5-side-plank-dips.gif',
                    # '6-oblique-leg-extensions.gif', '7-supermans.gif', '8-bridged-plank-leg-lifts.gif', '9-pushup.gif',
                    # '10-heel-touches.gif', '11-bicycle.gif', '12-half-up-twists.gif']

# instantiate Slack & Twilio clients
# slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))

def handle_command(command, person, job_status, weekly_schedule):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    # time to set schedule on Sundays
    hour = 13; error_message = True

    if person.status == 'active' and person.name == 'stephen':
        during_workout(person)
    elif not person.routine and person.name == 'stephen':
        time_str = str(hour) + ':00'
        #
        # ------------------ really need to make this more dynamic to user's time ----------------#
        #
        message = 'hey @' + person.name + ', it looks like you don\'t a schedule set up yet. we\'ll do that for you ' \
            + 'on *sunday* at *' + time_str + '*.'
        time_str = str(hour + util.gmt_x_timezone[person.timezone]) + ':00'
        slack_client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
        # weekly_schedule.schedule.every().sunday.at(time_str).do(set_routine, person, schedule)
        weekly_schedule.schedule.every(1).minutes.do(set_routine, person, weekly_schedule)
        job_status = True
    else:
        message = 'we\'re still building out our functionality. come back in a few weeks.'
        slack_client.api_call('chat.postMessage', channel=person.channel, text=message, as_user=True)

    return job_status

def begin_workout(person, weekly_schedule):
    message = 'morning @' + person.name + ', you ready for your workout?'
    slack_client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
    time.sleep(READ_WEBSOCKET_DEALY)
    response = None
    while response == None:
        response, _, _ = parse_slack_output(slack_client.rtm_read())
        time.sleep(READ_WEBSOCKET_DELAY)
    gmt_time = time.gmtime()
    hour = gmt_time[3] + 1
    minute = gmt_time[4]
    time_str = str(hour) + ':' + str(minute)
    if response.startswith('n'):
        message = 'you lazy piece of... just don\'t let it happen again'
        person.status = 'inactive'
    elif response.startswith('y'):
        message = 'that\'s what i wanted to hear! i\'ll check back in an hour'
        weekly_schedule.end_workout(person, time_str)
        person.status = 'active'
    else:
        message = 'i don\'t know what that means, so we\'re starting your workout anyways. i\'ll check back in an hour'
        weekly_schedule.end_workout(person, time_str)
        person.status = 'active'
    slack_client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)

def during_workout(person):
    message = 'don\'t talk to me, you should be working out!'
    slack_client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
    time.sleep(READ_WEBSOCKET_DELAY)

def end_workout(person):
    person.status = 'inactive'
    message = '@' + person.name + ', looks like you finished your workout. how many miles did you run?'
    slack_client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
    miles = None
    while miles == None:
        miles, _, _ = parse_slack_output(slack_client.rtm_read())
        time.sleep(READ_WEBSOCKET_DELAY)
    message = 'impressive. how long did you run for?'
    slack_client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
    duration = None
    while duration == None:
        duration, _, _ = parse_slack_output(slack_client.rtm_read())
        time.sleep(READ_WEBSOCKET_DELAY)
    message = 'nice. you ran ' + miles + ' miles in ' + duration + ' minutes'
    slack_client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
    time.sleep(READ_WEBSOCKET_DELAY)

    curr = time.strftime("%Y-%m-%d %H:%M:%S")
    DATABASE.execute("INSERT INTO my_running_table VALUES (?, ?, ?, ?, ?)",
        (person.name, curr, float(miles), float(duration), float(duration) / float(miles)))
    CONNECTION.commit()
    print '[main.end_workout(person)]: adding workout statistics for ' + person.name

def parse_slack_output(slack_rtm_output):
    """
    The Slack Real Time Messaging API is an events firehose.
    this parsing function returns None unless a message is
    directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:

            _, gym_bot_channels = util.get_list_of_channels(slack_client)

            if output and 'text' in output:
                if BOT_ID != output['user'] and output['channel'] in gym_bot_channels:
                    return output['text'].lower(), output['channel'], output['user']
                elif output and 'text' in output and AT_BOT in output['text']:
                    # return text after the @ mention, whitespace removed
                    return output['text'].split(AT_BOT)[1].strip().lower(), \
                        output['channel'], output['user']
    return None, None, None

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
            start_time, channel, user_name = parse_slack_output(slack_client.rtm_read())
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
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    sqlite_path = os.getcwd() + '/'    # name of the sqlite database file

    if len(sys.argv) < 2:
        print('Usage:')
        print('  python {} <database name>'.format(sys.argv[0]))
        exit()

    sqlite_file = sqlite_path + sys.argv[1]
    CONNECTION  = sqlite3.connect(sqlite_file)
    DATABASE    = CONNECTION.cursor()

    weekly_schedule = scheduler.Scheduler()

    if slack_client.rtm_connect():
        print('\n--- gym-buddy connected and running! ---\n')
        ids_x_person = util.get_list_of_users(slack_client)
        bot_channels, _ = util.get_list_of_channels(slack_client)

        # create each Person
        for i in ids_x_person:
            if i in [BOT_ID, 'USLACKBOT']:
                temp = person.Person(i, ids_x_person[i][0], ids_x_person[i][1].lower(), 'n/a')
            else:
                temp = person.Person(i, ids_x_person[i][0], ids_x_person[i][1].lower(), bot_channels[i])
            ids_x_person[i] = temp

        jobs_scheduled = False
        while True:
            ''' need to send start of workout message here '''
            for i in ids_x_person:
                if ids_x_person[i].status == 'start' and ids_x_person[i].name == 'stephen':
                    begin_workout(ids_x_person[i], weekly_schedule)
                elif ids_x_person[i].status == 'complete' and ids_x_person[i].name == 'stephen':
                    end_workout(ids_x_person[i])
            try:
                command, channel, user_id = parse_slack_output(slack_client.rtm_read())
            except websocket._exceptions.WebSocketConnectionClosedException:
                print 'Error Caught: Connnection is already closed.'
                sys.exit()

            if command and channel:
                jobs_scheduled = handle_command(command, ids_x_person[user_id], jobs_scheduled, weekly_schedule)
            if jobs_scheduled:
                weekly_schedule.run_pending()
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print 'Connection failed. Invalid Slack token or bot ID?'

    CONNECTION.commit()
    CONNECTION.close()
