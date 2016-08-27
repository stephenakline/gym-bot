import string
import schedule
import sqlite3
import sys
import util

class Person:

    def __init__(self, slack_id, name, timezone, channel, sqlite_file):
        """ initialize a person by taking in data """

        self.slack_id = slack_id
        self.name     = name
        self.timezone = timezone
        self.channel  = channel
        self.routine  = {}
        self.status   = 'inactive'
        self.conn     = sqlite3.connect(sqlite_file)

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

    def finish_workout(self):
        print '[person.end_workout()]: ending workout for ' + self.name
        self.status = 'complete'
        return schedule.CancelJob

    def summary_report(self):
        # connecting to the database file
        c = self.conn.cursor()

        # print all records for person from running table
        c.execute('SELECT * FROM my_running_table WHERE user_id == \'' + self.name + '\'')
        all_rows = c.fetchall()
        print "my_running_table:"
        for i in all_rows:
            print 'user_id: '     + str(i[0])
            print '\tdate_time: ' + str(i[1])
            print '\tdistance: '  + str(i[2])
            print '\tduration: '  + str(i[3])
            print '\tmile_time: ' + str(i[4])

        # print all records for person from workout table
        c.execute('SELECT * FROM my_workout_table WHERE user_id == \'' + self.name + '\'')
        all_rows = c.fetchall()
        print "\nmy_workout_table:"
        for i in all_rows:
            print 'user_id: '       + str(i[0])
            print '\tdate_time: '   + str(i[1])
            print '\trepetitions: ' + str(i[2])

        # close connection to database
        self.conn.commit()
        self.conn.close()

    def __repr__(self):
        """ overloading of print method for Person class """

        string = self.name + " is currently located in " + self.timezone + \
            " and talks to gym-buddy in " + self.channel + ". their schedule is as follows: \n"
        for i in self.routine:
            string += "\ton " + i + ", will workout at " + self.routine[i] + ".\n"
        return string
