""" data objects """
gmt_x_timezone = {}
gmt_x_timezone['eastern daylight yime'] = -4
gmt_x_timezone['central'] = -5
gmt_x_timezone['mountain'] = -6
gmt_x_timezone['pacific daylight time'] = -7
list_timezones = ""
for i in gmt_x_timezone.keys():
    list_timezones += '*' + i.title() + '*, '
list_timezones = list_timezones[:-2]

days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

""" helper functions for splitting up unicode and getting list fo users/channels """
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
