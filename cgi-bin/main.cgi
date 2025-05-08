#!/usr/bin/env python3
import os
import http.cookies
import sqlite3

print("Content-Type: text/html")
print()

# Check cookie
cookies = http.cookies.SimpleCookie(os.environ.get("HTTP_COOKIE"))
session_id = cookies.get("session_id")

conn = sqlite3.connect("/tmp/servers.db")
c = conn.cursor()

username = None
if session_id:
    session_val = session_id.value
    c.execute("SELECT username FROM sessions WHERE session_id = ?", (session_val,))
    row = c.fetchone()
    if row:
        username = row[0]

if not username:
    print("""
    <html>
    <head><title>Login Required</title></head>
    <body>
      <h2>Login Required</h2>
      <form action='/cgi-bin/login.cgi' method='POST'>
        <input type='text' name='username' placeholder='Enter username' required />
        <input type='submit' value='Login' />
      </form>
    </body></html>
    """)
    exit()

# Show user's servers
c.execute("SELECT id, description, ready FROM servers WHERE owner = ?", (username,))
rows = c.fetchall()
print(f"""
<html>
<head><title>{username}'s Servers</title></head>
<body>
  <h2>Welcome, {username}</h2>
  <form action='/cgi-bin/create_server.cgi' method='POST'>
    <input type='text' name='desc' placeholder='Description'>
    <input type='submit' value='Create Server'>
  </form>
  <h3>Your Servers:</h3>
  <ul>
""")
for row in rows:
    server_id, desc, ready = row
    status = "Ready" if ready else "Initializing..."
    print(f"<li>Server #{server_id} - {desc} - {status} <form style='display:inline;' action='/cgi-bin/terminate_server.cgi' method='POST'><input type='hidden' name='id' value='{server_id}'><input type='submit' value='Terminate'></form></li>")

print("""
  </ul>
</body>
</html>
""")
