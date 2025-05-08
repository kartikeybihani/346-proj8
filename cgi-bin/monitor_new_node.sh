#!/bin/bash

SERVER_ID=$1
INSTANCE_ID=$2

sleep 30
sqlite3 /tmp/servers.db "UPDATE servers SET ready=1 WHERE id=$SERVER_ID;"

