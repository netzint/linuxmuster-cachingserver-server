#!/usr/bin/env python3
#
# by lukas.spitznagel@netzint.de
#

import json
import os

def ifServerExistInSecretFile(name):
    if os.path.exists("/var/lib/linuxmuster-cachingserver/cachingserver_rsync.secrets"):
        with open("/var/lib/linuxmuster-cachingserver/cachingserver_rsync.secrets") as f:
            if name in f.read():
                return True
    return False

print("# Migrating server list to rsync file...")

with open("/var/lib/linuxmuster-cachingserver/servers.json") as f:
    servers = json.load(f)
    for server in servers:
        if not ifServerExistInSecretFile(servers[server]["name"]):
            print(f"# Add {servers[server]['name']} to rsync file...", end="")
            with open("/var/lib/linuxmuster-cachingserver/cachingserver_rsync.secrets", "a") as f2:
                f2.write(servers[server]["name"] + ":" + servers[server]["secret"] + "\n")
            os.chmod("/var/lib/linuxmuster-cachingserver/cachingserver_rsync.secrets", 600)
            print(" ok")