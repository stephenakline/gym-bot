'''
File that contains functions [...]
'''
import time
from slackclient import SlackClient

import person
import util
import scheduler

READ_WEBSOCKET_DELAY = 1

'''
Global Variables
'''
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

'''
If user has said yes to working out, then ask question to deterine which workout.
User is then sent down a line of questions depending on the workout.
TODO add functions for body-weight workouts
'''
# def determine_workout(respone, person, weekly_schedule):

'''
This function begins the discussion about a workout. If user says 'yes' it then determines
what workout the user is going to do that day by calling 'determine_workout'. If the user
says no, we do not run the workout.
TODO add function to count the number of times a user does or does not workout
TODO make time more dynamic for end of workout
'''
def begin(person, weekly_schedule, slack_client):
    message = 'morning @' + person.name + ', you ready for your workout?'
    slack_client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
    time.sleep(READ_WEBSOCKET_DELAY)
    response = None
    while response == None:
        response, _, _ = util.parse_slack_output(slack_client.rtm_read(), slack_client)
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

'''
Function that responds to user while they are working out.
'''
def during(person, slack_client):
    message = 'don\'t talk to me, you should be working out!'
    slack_client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
    time.sleep(READ_WEBSOCKET_DELAY)

'''
Placeholder for end of body workout. Need to determine how we want conversation to go
during the body workout routine
TODO see above
'''
def end(person, slack_client):
    person.status = 'inactive'
    message = '@' + person.name + ', looks like you finished your workout. how many miles did you run?'
    slack_client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
    miles = None
    while miles == None:
        miles, _, _ = util.parse_slack_output(slack_client.rtm_read(), slack_client)
        time.sleep(READ_WEBSOCKET_DELAY)
    message = 'impressive. how long did you run for?'
    slack_client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
    duration = None
    while duration == None:
        duration, _, _ = util.parse_slack_output(slack_client.rtm_read(), slack_client)
        time.sleep(READ_WEBSOCKET_DELAY)
    message = 'nice. you ran ' + miles + ' miles in ' + duration + ' minutes'
    slack_client.api_call('chat.postMessage', channel = person.channel, text = message, as_user = True, link_names = 1)
    time.sleep(READ_WEBSOCKET_DELAY)

    curr = time.strftime("%Y-%m-%d %H:%M:%S")
    DATABASE.execute("INSERT INTO my_running_table VALUES (?, ?, ?, ?, ?)",
        (person.name, curr, float(miles), float(duration), float(duration) / float(miles)))
    CONNECTION.commit()
    print '[workout.end(person)]: adding workout statistics for ' + person.name

'''
After running workout is complete, user is ask questions to record into data base.
'''
# def end_running_workout(person):
