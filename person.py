import string
import schedule
import sys
import util

class Person:

    def __init__(self, slack_id, name, timezone, channel):
        """ initialize a person by taking in data """

        self.slack_id = slack_id
        self.name     = name
        self.timezone = timezone
        self.channel  = channel
        self.routine  = {}
        self.status   = 'inactive'

    def set_timezone(self, timezone):
        self.timezone = timezone

    def get_local_time(self, gmt_time):
        hour = int(gmt_time.split(":")[0]) + util.gmt_x_timezone[self.timezone]
        minute = gmt_time.split(":")[1]
        return str(hour) + ':' + str(minute)

    def set_routine(self, time_str, day):
        print '[person.set_routine(time_str, day)]: set routine for ' + self.name + ' at ' \
            + day + ', ' + Person.get_local_time(self, time_str) + ' ' + self.timezone
        self.routine[day] = time_str

    def start_workout(self):
        print '[person.start_workout()]: starting workout for ' + self.name
        self.status = 'start'
        return schedule.CancelJob

    def end_workout(self):
        print '[person.end_workout()]: ending workout for ' + self.name
        self.status = 'complete'
        return schedule.CancelJob

    # move this to Person class?
    def get_running_data(self):
        distance = None
        question = "How many miles did you run today?"
        slack_client.api_call("chat.postMessage", channel=self.channel, text=question, as_user=True)
        while distance == None:
            distance, _, _ = parse_slack_output(slack_client.rtm_read())
            time.sleep(READ_WEBSOCKET_DELAY)

        try:
            distance = float(distance)
        except ValueError:
            # Handle the exception
            response = "Try again " + self.name + ", you gotta enter a number."
            slack_client.api_call("chat.postMessage", channel=self.channel, text=response, as_user=True)
            return

        duration = None
        question = ""
        if random.random() < .2:
            question = "Awesome. "
        elif random.random() < .4:
            question = "Impressive. "
        question += "How many minutes did you run for?"
        slack_client.api_call("chat.postMessage", channel=self.channel, text=question, as_user=True)
        while duration == None:
            duration, _, _ = parse_slack_output(slack_client.rtm_read())
            time.sleep(READ_WEBSOCKET_DELAY)

        try:
            duration = float(duration)
        except ValueError:
            # Handle the exception
            response = "Try again " + self.name + ", you gotta enter a number."
            slack_client.api_call("chat.postMessage", channel=self.channel, text=response, as_user=True)
            return

        pace = duration / distance
        best_pace = get_best_pace(c)

        if pace <= best_pace:
            response = "Amazing, you ran a *" + str(round(pace, 2)) + "* minute mile! That's new personal best!"
        else:
            response = "Not bad, you ran a *" + str(round(pace, 2)) + "* minute mile!"

        slack_client.api_call("chat.postMessage", channel=self.channel, text=response, as_user=True)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        database.execute("INSERT INTO my_running_table VALUES (?, ?, ?, ?, ?)",
            (self.name, current_time, distance, duration, pace))
        conn.commit()

    def __repr__(self):
        """ overloading of print method for Person class """

        string = self.name + " is currently located in " + self.timezone + \
            " and talks to gym-buddy in " + self.channel + ". their schedule is as follows: \n"
        for i in self.routine:
            string += "\ton " + i + ", will workout at " + self.routine[i] + ".\n"
        return string

'''
# move this to Person class?
def get_workout_statistics(channel, database, ids_x_names):
    for i in WORKOUT_LIST:
        filepath = os.getcwd() + '/workout/' + i
        title = "'" + WORKOUT_LIST[i] + "'"
        comment = "'How many " + WORKOUT_LIST[i] + " did you do?'"
        display_file_to_slack(filepath, channel, title, comment)
        reps = None
        while reps == None:
            reps, channel, user_name = parse_slack_output(slack_client.rtm_read())
            time.sleep(READ_WEBSOCKET_DELAY)

        try:
            reps = int(reps)
        except ValueError:
            # Handle the exception
            response = "come on now " + ids_x_names[user_name] + ", you gotta enter a number."
            slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
            return

        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        # database.execute("INSERT INTO my_workout_table VALUES (?, ?, ?)", (user_name, current_time, reps))
        # conn.commit()
        print "store information for " + i + "in my_workout_table for " + ids_x_names[user_name]

    if any(x in command for x in RUN_COMMAND):
        get_running_statistics(database, person)
        response = None
    elif any(x in command for x in ROW_COMMAND):
        response = "I don't have the row data base set up yet - try again in a few weeks."
    elif any(x in command for x in WORKOUT_COMMAND):
        # get_workout_statistics(channel, database, person)
        response = "I don't have the workout data base set up yet - try again in a few weeks."
    elif any(x in command for x in SUMMARY_COMMAND):
        # display_file_to_slack(os.getcwd() + '/images/bravo-congrats.gif', person.get_channel(), 'Wow! Bravo!', 'Your summary will be coming soon...')
        response = "I don't have the summary set up yet - tray again in a few weeks."
    else:
        response = "Not sure what you mean. Use either *" + RUN_COMMAND[0] + \
            "*, *" + ROW_COMMAND[0] + "* or *" + WORKOUT_COMMAND[0] + \
            "* to start recording data. If you want a summary report, " \
            "say *" + SUMMARY_COMMAND[0] + "*."

    if response != None and error_message:
        slack_client.api_call("chat.postMessage", channel=person.get_channel(),
            text=response, as_user=True)

'''
