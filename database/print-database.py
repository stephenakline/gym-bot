import os
import sqlite3
import sys

sqlite_path = os.getcwd() + '/database/'  # name of the sqlite database file

if len(sys.argv) < 2:
  print('Usage:')
  print('  python {} <database name>'.format(sys.argv[0]))
  exit()

sqlite_file = sqlite_path + sys.argv[1]

# Connecting to the database file
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

c.execute('SELECT * FROM my_running_table')
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
