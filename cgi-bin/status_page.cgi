#!/usr/bin/env python3
import cgi
import cgitb
import sqlite3
import os
import http.cookies
from google.oauth2 import service_account
from googleapiclient import discovery

cgitb.enable()
print("Content-Type: text/html\n")

# Parse ID from URL
form = cgi.FieldStorage()
server_id = form.getfirst("id")

if not server_id:
    print("<html><body><h2>400 Bad Request: Missing server ID</h2></body></html>")
    exit()

# Session cookie check
cookies = http.cookies.SimpleCookie(os.environ.get("HTTP_COOKIE"))
session_id = cookies.get("session_id")

if not session_id:
    print("<html><body><h2>401 Unauthorized: No session</h2></body></html>")
    exit()

conn = sqlite3.connect("/tmp/servers.db")
c = conn.cursor()
c.execute("SELECT username FROM sessions WHERE session_id = ?", (session_id.value,))
sess_row = c.fetchone()

if not sess_row:
    print("<html><body><h2>401 Unauthorized: Invalid session</h2></body></html>")
    exit()

username = sess_row[0]

# Get server info
c.execute("SELECT id, owner, description, instance_id, ready FROM servers WHERE id = ?", (server_id,))
row = c.fetchone()
conn.close()

if not row:
    print("<html><body><h2>404 Not Found: No such server</h2></body></html>")
    exit()

sid, owner, desc, instance_id, ready = row

if owner != username:
    print("<html><body><h2>403 Forbidden: Not your server</h2></body></html>")
    exit()

# Get IP if ready
ip = "Not available"
if ready:
    try:
        creds = service_account.Credentials.from_service_account_file("/gcp_creds.json")
        compute = discovery.build("compute", "v1", credentials=creds)
        project = "lunar-box-292917"
        zone = "us-central1-a"
        result = compute.instances().get(project=project, zone=zone, instance=instance_id).execute()
        ip = result["networkInterfaces"][0]["accessConfigs"][0]["natIP"]
    except Exception as e:
        ip = f"Error fetching IP: {e}"

# Output HTML
print(f"""
<html>
<head><title>Status of Server #{sid}</title></head>
<body>
  <h2>Server Status Page</h2>
  <ul>
    <li><strong>ID:</strong> {sid}</li>
    <li><strong>Owner:</strong> {owner}</li>
    <li><strong>Description:</strong> {desc}</li>
    <li><strong>Status:</strong> {'Ready' if ready else 'Initializing'}</li>
    <li><strong>IP Address:</strong> {ip}</li>
  </ul>
  <a href='/cgi-bin/main.cgi'>Back to Dashboard</a>
</body>
</html>
""")