#!/usr/bin/env python3

#########################################################
# 
# by Netzint GmbH 2024
# Lukas Spitznagel (lukas.spitznagel@netzint.de)
# 
#########################################################

import json
import subprocess
import logging
import uvicorn
import os
import re

from fastapi import FastAPI
from pydantic import BaseModel

logging.basicConfig(filename='/var/log/linuxmuster/cachingserver/api.log',format='%(levelname)s: %(asctime)s %(message)s', level=logging.DEBUG)

with open("/var/lib/linuxmuster-cachingserver/servers.json") as f:
    config = json.load(f)

app = FastAPI()

class MACCT(BaseModel):
    macct: str

LINUXMUSTER_LDB_PATH = "--url=/var/lib/samba/private/sam.ldb"
LINUXMUSTER_LDB_OPTIONS = [
        "--nosync",
        "--verbose",
        "--controls=relax:0",
        "--controls=local_oid:1.3.6.1.4.1.7165.4.3.7:0",
        "--controls=local_oid:1.3.6.1.4.1.7165.4.3.12:0"
    ]

def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return result.stdout.strip()

@app.get("/v1/images/macct")
def get_macct_of_a_computer(computername: str):
    """
    Get the unicodePwd and the supplementalCredentials for the given computer.
    """

    if "." in computername:
        computername = computername.split(".")[0]

    computername = computername.upper()

    computer_unicodepwd = run_command(["/usr/bin/ldbsearch", LINUXMUSTER_LDB_PATH, "(&(sAMAccountName=" + computername + "$))", "unicodePwd"])
    computer_supplementalcredentials = run_command(["/usr/bin/ldbsearch", LINUXMUSTER_LDB_PATH, "(&(sAMAccountName=" + computername + "$))", "supplementalCredentials"])

    if computer_unicodepwd != None and computer_supplementalcredentials != None:
        computer_unicodepwd_match = re.search(r'unicodePwd:: (\S+)', computer_unicodepwd)
        computer_supplementalcredentials_match = re.search(r'supplementalCredentials:: ([\s\S]+?)(?=\n#|\nref:|\n\n)', computer_supplementalcredentials)
        if computer_unicodepwd_match and computer_supplementalcredentials_match:
            computer_unicodepwd = computer_unicodepwd_match.group(1)
            computer_supplementalcredentials = computer_supplementalcredentials_match.group(1).replace("\n", "").replace(" ", "")
            return {"status": True, "data": {"unicodepwd": computer_unicodepwd, "supplementalcredentials": computer_supplementalcredentials}}
    
    return {"status": False, "data": ""}

@app.post("/v1/images/macct")
def set_macct_of_a_computer(computername: str, macct: MACCT):
    """
    Set the macct file (unicodePwd and supplementalCredentials) for the given computer
    """

    if "." in computername:
        computername = computername.split(".")[0]

    computername = computername.upper()

    computer_dn = run_command(["/usr/bin/ldbsearch", LINUXMUSTER_LDB_PATH, "(&(sAMAccountName=" + computername + "$))", "dn"])
    if computer_dn == None:
        logging.error(f"Could not find dn for computer '{computername}'...")
        return {"status": False, "data": f"Could not find dn for computer '{computername}'..."}
    else:
        computer_dn_match = re.search(r'dn: (\S+)', computer_dn)
        if computer_dn_match:
            computer_dn = computer_dn_match.group(1)
            logging.info(f"Find dn '{computer_dn}' for computer '{computername}'")
        else:
            return {"status": False, "data": ""}

    LDIF_FILE = f"/var/tmp/.{computername}_macct.ldif"

    with open(LDIF_FILE, "w") as f:
        f.write(macct.macct.replace("@@dn@@", computer_dn))

    computer_modify = run_command(["/usr/bin/ldbmodify", LINUXMUSTER_LDB_PATH] + LINUXMUSTER_LDB_OPTIONS + [LDIF_FILE])
    os.remove(LDIF_FILE)

    if computer_modify == None:
        logging.error(f"Could not modify entry for computer '{computername}'...")
        return {"status": False, "data": f"Could not modify entry for computer '{computername}'..."}
    
    logging.info(f"Computer '{computername}' successfully modified!")
    return {"status": True, "data": f"Computer '{computername}' successfully modified!"}



#########################################

def main():
    logging.info("Starting Linuxmuster-Cachingserver-API on port 4456!")
    uvicorn.run(app, host="0.0.0.0", port=4456)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(e)