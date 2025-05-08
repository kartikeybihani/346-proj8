#!/usr/bin/env python3
import cgi
import cgitb
import os
import http.cookies
import sqlite3
from googleapiclient import discovery
from google.oauth2 import service_account

cgitb.enable()

print("Content-Type: text/plain\n")

# Validate session
cookies = http.cookies.SimpleCookie(os.environ.get("HTTP_COOKIE"))
session_id = cookies.get("session_id")

if not session_id:
    print("401 Unauthorized: No session.")
    exit()

conn = sqlite3.connect("/tmp/servers.db")
c = conn.cursor()
c.execute("SELECT username FROM sessions WHERE session_id = ?", (session_id.value,))
row = c.fetchone()

if not row:
    print("401 Unauthorized: Invalid session.")
    exit()

username = row[0]

# Get server ID
form = cgi.FieldStorage()
server_id = form.getfirst("id")

if not server_id:
    print("400 Bad Request: Missing server ID")
    exit()

# Check ownership
c.execute("SELECT instance_id FROM servers WHERE id = ? AND owner = ?", (server_id, username))
row = c.fetchone()

if not row:
    print("403 Forbidden: Not your server.")
    exit()

instance_id = row[0]

# Call GCP to delete instance
creds = service_account.Credentials.from_service_account_file("/gcp_creds.json")
compute = discovery.build("compute", "v1", credentials=creds)
project = "lunar-box-292917"
zone = "us-central1-a"

try:
    compute.instances().delete(project=project, zone=zone, instance=instance_id).execute()
except Exception as e:
    print(f"Warning: GCP deletion failed - {str(e)}")

# Remove from DB
c.execute("DELETE FROM servers WHERE id = ?", (server_id,))
conn.commit()
conn.close()

# Redirect back to main
print("Status: 302 Found")
print("Location: /cgi-bin/main.cgi\n")
print("Terminated.")