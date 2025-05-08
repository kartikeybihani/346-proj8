#!/usr/bin/env python3

import sys
import time
import sqlite3
from googleapiclient import discovery
from google.oauth2 import service_account

server_id = sys.argv[1]
instance_name = sys.argv[2]

project = "lunar-box-292917"
zone = "us-central1-a"

creds = service_account.Credentials.from_service_account_file("/gcp_creds.json")
compute = discovery.build("compute", "v1", credentials=creds)

# Wait for VM to be ready
while True:
    result = compute.instances().get(project=project, zone=zone, instance=instance_name).execute()
    status = result["status"]
    if status == "RUNNING":
        break
    time.sleep(5)

# Mark as ready in database
conn = sqlite3.connect("/tmp/servers.db")
c = conn.cursor()
c.execute("UPDATE servers SET ready=1 WHERE id=?", (server_id,))
conn.commit()
conn.close()
