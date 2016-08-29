import os
import sqlite3
import sys

sqlite_path = os.getcwd() + '/'  # name of the sqlite database file

if len(sys.argv) < 2:
  print('Usage:')
  print('  python {} <database name>'.format(sys.argv[0]))
  exit()

sqlite_file = sqlite_path + sys.argv[1]

# Connecting to the database file
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()



c.execute("SELECT * FROM my_running_table WHERE date_time BETWEEN \'" \
    + str(old_time) + "\' AND \'" + str(datetime.datetime.now()) + "\'" \
    + "AND user_id == \'stephen\'")

select * from test
 where date between '03/19/2014' and '03/19/2014 23:59:59'

all_rows = c.fetchall()
print "my_running_table:"
for i in all_rows:
	print "\t",
	print i

c.execute('SELECT * FROM my_workout_table')
all_rows = c.fetchall()
print "\nmy_workout_table:"
for i in all_rows:
	print "\t",
	print i

# Committing changes and closing the connection to the database file
conn.commit()
conn.close()
