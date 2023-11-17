import sqlite3

conn = sqlite3.connect('mydatabase.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS exploit_performance
             (id INTEGER PRIMARY KEY, exploit_name TEXT, exploit_arguments TEXT, flags_captured INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS ticks
             (timestamp INTEGER PRIMARY KEY, exploit_performance_id INTEGER, FOREIGN KEY(exploit_performance_id) REFERENCES exploit_performance(id))''')

c.execute("INSERT INTO exploit_performance (exploit_name, exploit_arguments, flags_captured) VALUES ('ExampleExploit', 'args', 3)")
conn.commit()

conn.close()
