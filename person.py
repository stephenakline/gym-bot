import os
import string
import sqlite3
import sys
import util
import datetime
from slackclient import SlackClient

import scheduler
import workout

class Person:

    def __init__(self, slack_id, name, timezone, channel, sqlite_file):
        """ initialize a person by taking in data """

        self.slack_id    = slack_id
        self.name        = name
        self.timezone    = timezone
        self.channel     = channel
        self.routine     = {}
        self.status      = 'inactive'
        self.conn        = sqlite3.connect(sqlite_file)
        self.client      = SlackClient(os.environ.get('SLACK_TOKEN'))
        self.my_schedule = scheduler.Scheduler()

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
        workout.begin(self)
        return schedule.CancelJob

    def finish_workout(self):
        print '[person.end_workout()]: ending workout for ' + self.name
        self.status = 'complete'
        workout.end(self)
        return schedule.CancelJob

    # TODO what other information does user want?
    # TODO add same thing for workout
    def summary_report(self):
        # connecting to the database file
        c = self.conn.cursor()

        last_week = datetime.datetime.now() - datetime.timedelta(days = 7)

        # print all records for person from running table
        c.execute('SELECT * FROM my_running_table WHERE date_time BETWEEN \'' \
            + str(last_week) + '\' AND \'' + str(datetime.datetime.now()) + '\'' \
            + 'AND user_id == \'' + self.name + '\'')

        all_rows = c.fetchall()
        total_miles = 0.0
        for i in all_rows:
            total_miles += i[3]

        # close connection to database
        self.conn.commit()
        self.conn.close()

        message = '@' + self.name + ', this past week you ran *' + str(total_miles) + ' miles*. not so great fat-ass. \nstep it up!'
        return message

    def __repr__(self):
        """ overloading of print method for Person class """

        string = self.name + " is currently located in " + self.timezone + \
            " and talks to gym-buddy in " + self.channel + ". their schedule is as follows: \n"
        for i in self.routine:
            string += "\ton " + i + ", will workout at " + self.routine[i] + ".\n"
        return string
