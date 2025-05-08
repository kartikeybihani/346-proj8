import sqlite3

conn = sqlite3.connect("/tmp/servers.db")
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner TEXT NOT NULL,
    description TEXT,
    instance_id TEXT,
    ready INTEGER
)
''')

# Sessions table for Project 8
c.execute('''
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    username TEXT NOT NULL
)
''')


conn.commit()
conn.close()
print("Database initialized.")
