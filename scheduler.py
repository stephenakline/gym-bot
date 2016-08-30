import sys
import schedule
from slackclient import SlackClient

class Scheduler:

    def __init__(self):
        """ initialize an instance of the Scheduler class """
        self.schedule = schedule

    def run_pending(self):
        self.schedule.run_pending()

    def start_persons_workout(self, person):
        for i in person.routine:
            if i == 'monday':
                self.start_monday_routine(person, person.routine[i])
            elif i == 'tuesday':
                self.start_tuesday_routine(person, person.routine[i])
            elif i == 'wednesday':
                self.start_wednesday_routine(person, person.routine[i])
            elif i == 'thursday':
                self.start_thursday_routine(person, person.routine[i])
            elif i == 'friday':
                self.start_friday_routine(person, person.routine[i])
            elif i == 'saturday':
                self.start_saturday_routine(person, person.routine[i])
            elif i == 'sunday':
                self.start_sunday_routine(person, person.routine[i])

    def end_workout(self, person, time_str):
        print '[scheduler.end_workout(person, time_str)]: workout ends for ' \
            + person.name + ' in 1 hour from ' + person.get_local_time(time_str) + ' ' + person.timezone
        hour = int(time_str.split(':')[0]) + 1
        minute = int(time_str.split(':')[0])
        time_end = str(hour) + ':' + str(minute)
        self.schedule.every().day.at(time_str).do(person.finish_workout)

    def start_monday_routine(self, person, time_str):
        print '[scheduler.start_monday_routine(person, time_str)]: workout starts for ' \
            + person.name + ' at ' + person.get_local_time(time_str) + ' ' + person.timezone
        self.schedule.every().monday.at(time_str).do(person.start_workout)

    def start_tuesday_routine(self, person, time_str):
        print '[scheduler.start_tuesday_routine(person, time_str)]: workout starts for ' \
            + person.name + ' at ' + person.get_local_time(time_str) + ' ' + person.timezone
        self.schedule.every().tuesday.at(time_str).do(person.start_workout)

    def start_wednesday_routine(self, person, time_str):
        print '[scheduler.start_wednesday_routine(person, time_str)]: workout starts for ' \
            + person.name + ' at ' + person.get_local_time(time_str) + ' ' + person.timezone
        self.schedule.every().wednesday.at(time_str).do(person.start_workout)

    def start_thursday_routine(self, person, time_str):
        print '[scheduler.start_thursday_routine(person, time_str)]: workout starts for ' \
            + person.name + ' at ' + person.get_local_time(time_str) + ' ' + person.timezone
        self.schedule.every().thursday.at(time_str).do(person.start_workout)

    def start_friday_routine(self, person, time_str):
        print '[scheduler.start_friday_routine(person, time_str)]: workout starts for ' \
            + person.name + ' at ' + person.get_local_time(time_str) + ' ' + person.timezone
        self.schedule.every().friday.at(time_str).do(person.start_workout)

    def start_saturday_routine(self, person, time_str):
        print '[scheduler.start_saturday_routine(person, time_str)]: workout starts for ' \
            + person.name + ' at ' + person.get_local_time(time_str) + ' ' + person.timezone
        self.schedule.every().saturday.at(time_str).do(person.start_workout)

    def start_sunday_routine(self, person, time_str):
        print '[scheduler.start_sunday_routine(person, time_str)]: workout starts for ' \
            + person.name + ' at ' + person.get_local_time(time_str) + ' ' + person.timezone
        self.schedule.every().sunday.at(time_str).do(person.start_workout)
