#!/usr/bin/env python3
import cgi
import uuid
import sqlite3

form = cgi.FieldStorage()
username = form.getfirst("username")

if not username:
    print("Status: 400 Bad Request")
    print("Content-Type: text/plain\n")
    print("Missing username")
    exit()

session_id = str(uuid.uuid4())

conn = sqlite3.connect("/tmp/servers.db")
c = conn.cursor()
c.execute("INSERT INTO sessions (session_id, username) VALUES (?, ?)", (session_id, username))
conn.commit()
conn.close()

print(f"Set-Cookie: session_id={session_id}; Path=/; HttpOnly")
print("Content-Type: text/html\n")
print("<html><body><script>window.location='/cgi-bin/main.cgi';</script></body></html>")