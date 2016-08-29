import os
import sqlite3

sqlite_file   = os.getcwd() + '/database/temp.sqlite'
table_run     = 'my_running_table'
table_row     = 'my_rowing_table'
table_workout = 'my_workout_table'

# Connecting to the database file
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

# Creating a new SQLite table with 1 column
c.execute('CREATE TABLE {tn} ({nf} {ft})'.format(tn=table_run, nf="user_id", ft="TEXT"))
c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}'".format(tn=table_run, cn="date_time", ft="DATETIME"))
c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}'".format(tn=table_run, cn="time_zone", ft="TEXT"))
c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn=table_run, cn="distance", ct="REAL"))
c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn=table_run, cn="duration", ct="REAL"))
c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn=table_run, cn="mile_time", ct="REAL"))

c.execute('CREATE TABLE {tn} ({nf} {ft})'.format(tn=table_workout, nf="user_id", ft="TEXT"))
c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}'".format(tn=table_workout, cn="date_time", ft="DATETIME"))
c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}'".format(tn=table_workout, cn="time_zone", ft="TEXT"))
c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn=table_workout, cn="repetitions", ct="INTEGER"))

# Committing changes and closing the connection to the database file
conn.commit()
conn.close()
