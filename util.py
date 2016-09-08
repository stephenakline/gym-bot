import os
import datetime

""" data objects """
# starterbot's ID as an environment variable
BOT_ID = os.environ.get('BOT_ID')
AT_BOT = "<@" + str(BOT_ID) + ">:"

TESTING_CHANNEL = 'G1YDKSM27'

gmt_x_timezone = {}
gmt_x_timezone['eastern daylight yime'] = -4
gmt_x_timezone['central'] = -5
gmt_x_timezone['mountain'] = -6
gmt_x_timezone['pacific daylight time'] = -7
list_timezones = ""
for i in gmt_x_timezone.keys():
    list_timezones += '*' + i.title() + '*, '
list_timezones = list_timezones[:-2]

list_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
days_number = [0, 1, 2, 3, 4, 5, 6]
days_of_week = dict(zip(list_days, days_number))

""" helper functions for splitting up unicode and getting list fo users/channels """
def parse_slack_output(slack_rtm_output, slack_client):
    """
    The Slack Real Time Messaging API is an events firehose.
    this parsing function returns None unless a message is
    directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            _, gym_bot_channels = get_list_of_channels(slack_client)
            if output and 'text' in output:
                if BOT_ID != output['user'] and output['channel'] in gym_bot_channels:
                    return output['text'].lower(), output['channel'], output['user']
                elif output and 'text' in output and AT_BOT in output['text']:
                    # return text after the @ mention, whitespace removed
                    return output['text'].split(AT_BOT)[1].strip().lower(), \
                        output['channel'], output['user']
    return None, None, None

def split_up_unicode(text):
	clean_version = text.split(':')[-1].strip('"')
        return clean_version

def get_list_of_users(slack_client):
    temp = slack_client.server.api_call("users.list")
    n = [e.encode('utf-8') for e in temp.strip('[]').split(',')]

    ids = []
    user_names = []
    time_zone = []

    for i in n:
        if i.startswith('{"id') or i.startswith('"members":[{"id":'):
            ids.append(split_up_unicode(i))
        if i.startswith('"name'):
            user_names.append(split_up_unicode(i))
        if i.startswith('"tz_label":'):
            time_zone.append(split_up_unicode(i))

    ids_x_names = dict(zip(ids, zip(user_names, time_zone)))
    return ids_x_names

def get_list_of_channels(slack_client):
    temp = slack_client.server.api_call("im.list")
    channel_info = [e.encode('utf-8') for e in temp.strip('[]').split(',')]

    channels = []
    users    = []

    for i in channel_info:
        if i.startswith('{"id') or i.startswith('"ims":[{'):
            channels.append(split_up_unicode(i))
        if i.startswith('"user":'):
            users.append(split_up_unicode(i))

    direct_channels = dict(zip(users, channels))
    return direct_channels, channels

def next_weekday(d, weekday, hour, minute):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    temp_date = str(d + datetime.timedelta(days_ahead)).split()[0]
    begin = temp_date + 'T' + str(hour).zfill(2) + ':' + str(minute).zfill(2) + ':00'
    end   = temp_date + 'T' + str(hour+1).zfill(2) + ':' + str(minute).zfill(2) + ':00'
    return [str(begin), str(end)]

""" JSON files for attachments such as images and buttons """

" data to make buttons (eventually) "
east = {}
east['name'] = 'east'
east['text'] = 'Eastern'
east['type'] = 'button'
east['value'] = 'east'
central = {}
central['name'] = 'central'
central['text'] = 'Central'
central['type'] = 'button'
central['value'] = 'central'
mountain = {}
mountain['name'] = 'mountain'
mountain['text'] = 'Mountain'
mountain['type'] = 'button'
mountain['value'] = 'mountain'
pacific = {}
pacific['name'] = 'pacific'
pacific['text'] = 'Pacific'
pacific['type'] = 'button'
pacific['value'] = 'pacific'

buttons = {}
buttons['text'] = 'select a timezone'
buttons['fallback'] = 'if you see this please contact stephen'
buttons['attachment_type'] = 'default'
buttons['callback_id'] = 'timezone_area'
buttons['actions'] = [east, central, mountain, pacific]
buttons = [buttons]
