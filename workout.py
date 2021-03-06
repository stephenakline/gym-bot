'''
File that contains functions [...]
'''
import datetime
import sqlite3
import time
from slackclient import SlackClient

import person
import util
import scheduler

'''
Global Variables
'''
READ_WEBSOCKET_DELAY = 1

class Workout:

    def __init__(self, connection):
        """ initialize an instance of the Scheduler class """
        self.run_command = ["run", "ran", "treadmill"]
        self.workout_command = ["workout"]
        self.connection = connection

# SUMMARY_COMMAND = ["summary", "report"]
# WORKOUT_LIST    = {'2-knee-up-crunches.gif': 'knee up crunches',
#                    '1-standard-crunch.gif': 'standard crunches'}
#                     #, '3-hip-lifts.gif',
#                     # '4-oblique-crunches.gif', '5-side-plank-dips.gif',
#                     # '6-oblique-leg-extensions.gif', '7-supermans.gif', '8-bridged-plank-leg-lifts.gif', '9-pushup.gif',
#                     # '10-heel-touches.gif', '11-bicycle.gif', '12-half-up-twists.gif']

    '''
    This function begins the discussion about a workout. If user says 'yes' it then determines
    what workout the user is going to do that day by calling 'determine_workout'. If the user
    says no, we do not run the workout.
    TODO add function to count the number of times a user does or does not workout
    TODO add function to provide pictures for workout
    TODO make time more dynamic for end of workout
    '''
    def begin(self, person):
        message = 'morning @' + person.name + ', you ready for your workout? if so, say *run* or *workout*. otherwise say no'
        person.client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
        time.sleep(READ_WEBSOCKET_DELAY)
        response = None
        while response == None:
            response, _, _ = util.parse_slack_output(person.client.rtm_read(), person.client)
            time.sleep(READ_WEBSOCKET_DELAY)
        gmt_time = time.gmtime()
        hour = gmt_time[3] + 1
        minute = gmt_time[4]
        time_str = str(hour) + ':' + str(minute)
        if response.startswith('n'):
            message = 'you lazy piece of shit. just don\'t let it happen again'
            person.status = 'inactive'
        elif response.startswith('r'):
            message = 'that\'s what i wanted to hear! good luck with the run, i\'ll check back in an hour'
            person.my_schedule.end_running_workout(person, time_str)
            person.status = 'active'
        elif response.startswith('w'):
            message = 'okay, let\'s do the around the world routine'
            person.my_schedule.end_workout(person, time_str)
            person.status = 'active'
        else:
            message = 'i don\'t know what that means, so we\'re starting your workout anyways. i\'ll check back in an hour'
            person.my_schedule.end_workout(person, time_str)
            person.status = 'active'
        person.client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)

    '''
    Function that responds to user while they are working out.
    '''
    def during(self, person):
        message = 'don\'t talk to me, you should be working out!'
        person.client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
        time.sleep(READ_WEBSOCKET_DELAY)

    '''
    Function that engages users at end of workout and records the miles and time spent running.
    '''
    def end_run(self, person):
        database = self.connection.cursor()

        person.status = 'inactive'
        message = '@' + person.name + ', looks like you finished your run. how many miles did you do?'
        person.client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
        miles = None
        while miles == None:
            miles, _, _ = util.parse_slack_output(person.client.rtm_read(), person.client)
            time.sleep(READ_WEBSOCKET_DELAY)
        message = 'impressive. how long did you run for?'
        person.client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
        duration = None
        while duration == None:
            duration, _, _ = util.parse_slack_output(person.client.rtm_read(), person.client)
            time.sleep(READ_WEBSOCKET_DELAY)
        message = 'nice. you ran ' + miles + ' miles in ' + duration + ' minutes'
        person.client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
        time.sleep(READ_WEBSOCKET_DELAY)

        current_date_time = str(datetime.datetime.now())
        database.execute("INSERT INTO my_running_table VALUES (?, ?, ?, ?, ?, ?)",
            (person.name, current_date_time, person.timezone, float(miles), float(duration), float(duration) / float(miles)))
        self.connection.commit()
        print '[workout.end_run(person)]: adding running statistics for ' + person.name

    '''
    Function that engages users at end of workout and records the number of repitions.
    '''
    def end_workout(self, person):
        database = self.connection.cursor()

        person.status = 'inactive'
        message = '@' + person.name + ', looks like you finished your workout. how many reps did you do?'
        person.client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
        repetitions = None
        while repetitions == None:
            repetitions, _, _ = util.parse_slack_output(person.client.rtm_read(), person.client)
            time.sleep(READ_WEBSOCKET_DELAY)

        current_date_time = str(datetime.datetime.now())
        database.execute("INSERT INTO my_workout_table VALUES (?, ?, ?, ?)",
           (person.name, current_date_time, person.timezone, float(repetitions)))
        self.connection.commit()
        print '[workout.end_workout(person)]: adding workout statistics for ' + person.name
