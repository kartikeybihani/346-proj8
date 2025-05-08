#!/usr/bin/env python3

import cgi
import cgitb
import sqlite3
import os
import uuid
import http.cookies
from googleapiclient import discovery
from google.oauth2 import service_account

cgitb.enable()

# Read session cookie
cookies = http.cookies.SimpleCookie(os.environ.get("HTTP_COOKIE"))
session_id = cookies.get("session_id")

if not session_id:
    print("Status: 401 Unauthorized")
    print("Content-Type: text/plain\n")
    print("No session cookie found.")
    exit()

conn = sqlite3.connect("/tmp/servers.db")
c = conn.cursor()
c.execute("SELECT username FROM sessions WHERE session_id = ?", (session_id.value,))
row = c.fetchone()

if not row:
    print("Status: 401 Unauthorized")
    print("Content-Type: text/plain\n")
    print("Invalid session.")
    exit()

user = row[0]

# Read description
form = cgi.FieldStorage()
desc = form.getfirst("desc", "")

# Setup GCP
creds = service_account.Credentials.from_service_account_file("/gcp_creds.json")
compute = discovery.build("compute", "v1", credentials=creds)

project = "lunar-box-292917"
zone = "us-central1-a"
name = f"proj7-instance-{uuid.uuid4().hex[:8]}"

config = {
   "name": name,
   "machineType": f"zones/{zone}/machineTypes/e2-micro",
   "disks": [{
       "boot": True,
       "autoDelete": True,
       "initializeParams": {
           "sourceImage": "projects/debian-cloud/global/images/family/debian-11"
       }
   }],
   "networkInterfaces": [{
       "network": "global/networks/default",
       "accessConfigs": [{"type": "ONE_TO_ONE_NAT", "name": "External NAT"}]
   }]
}

operation = compute.instances().insert(
   project=project, zone=zone, body=config).execute()

instance_id = name

# Save to DB
c.execute("INSERT INTO servers (owner, description, instance_id, ready) VALUES (?, ?, ?, ?)",
          (user, desc, instance_id, 0))
conn.commit()
server_id = c.lastrowid
conn.close()

# Start monitor script
os.system(f"/usr/local/bin/python3 /var/www/cgi-bin/monitor_new_node.py {server_id} {name} 1>/tmp/monout.log 2>/tmp/monerr.log &")

# Proper redirect using HTTP header
print("Status: 302 Found")
print("Location: /cgi-bin/main.cgi")
print("Content-Type: text/html\n")
print("Redirecting...")
