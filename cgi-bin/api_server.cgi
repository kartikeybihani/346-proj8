#!/usr/bin/env python3

import cgi
import cgitb
import sqlite3
import json
from google.oauth2 import service_account
from googleapiclient import discovery

cgitb.enable()
print("Content-Type: application/json\n")

# GCP credentials and configuration
creds = service_account.Credentials.from_service_account_file('/gcp_creds.json')
project = "lunar-box-292917"
zone = "us-central1-a"

form = cgi.FieldStorage()
server_id = form.getfirst("id")

conn = sqlite3.connect("/tmp/servers.db")
c = conn.cursor()

if server_id:
    c.execute("SELECT id, owner, description, instance_id, ready FROM servers WHERE id=?", (server_id,))
    row = c.fetchone()
    if not row:
        print(json.dumps({"error": "Server not found"}))
    else:
        if row[4] == 1:  # ready == 1
            instance_name = row[3]
            compute = discovery.build("compute", "v1", credentials=creds)
            result = compute.instances().get(
                project=project, zone=zone, instance=instance_name).execute()
            ip = result["networkInterfaces"][0]["accessConfigs"][0]["natIP"]
        else:
            ip = ""
        data = {
            "id": row[0],
            "owner": row[1],
            "description": row[2],
            "ip": ip
        }
        print(json.dumps(data))
else:
    c.execute("SELECT id, owner, description, instance_id, ready FROM servers")
    rows = c.fetchall()
    servers = []
    for row in rows:
        if row[4] == 1:  # ready == 1
            instance_name = row[3]
            compute = discovery.build("compute", "v1", credentials=creds)
            result = compute.instances().get(
                project=project, zone=zone, instance=instance_name).execute()
            ip = result["networkInterfaces"][0]["accessConfigs"][0]["natIP"]
        else:
            ip = ""
        servers.append({
            "id": row[0],
            "owner": row[1],
            "description": row[2],
            "ip": ip
        })
    print(json.dumps(servers))
