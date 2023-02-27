#!/usr/bin/env python3

#########################################################
# 
# by Netzint GmbH 2023
# Lukas Spitznagel (lukas.spitznagel@netzint.de)
# 
#########################################################

import socket
import logging
import json
import os
import argparse
import subprocess

from subprocess import PIPE

logging.basicConfig(filename='/var/log/linuxmuster/cachingserver/client.log',format='%(levelname)s: %(asctime)s %(message)s', level=logging.DEBUG)

def sendMessage(conn, msg):
    logging.debug(f"Send message '{msg}'")
    conn.send(msg.encode("utf-8"))

def receiveMessage(conn):
    message = conn.recv(1024).decode()
    if len(message) > 40:
        logging.debug("Receive message '" + message[:40].replace('\n', '') + "...'")
    else:
        logging.debug(f"Receive message '{message}'")
    return message

def getRegisteredServers():
    file = open("/var/lib/linuxmuster-cachingserver/servers.json", "r")
    json_result = json.load(file)
    file.close()
    return json_result

def connect(ip, port):
    logging.info(f"Starting new connection to {ip} on port {port}...")
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip, port))
        logging.info("Connection successful!")
        return client
    except Exception as e:
        logging.error(f"Connection to {ip} on port {port} not possible! Message: " + str(e))
        return False

def authenticate(client, key):
    sendMessage(client, "auth %s" % key)
    result = receiveMessage(client).split(" ", 1)

    if result[0] != "hello":
        logging.error(f"Authentification failed! Connection to {client.getpeername()[0]} is not possible!")
        return False

    logging.info("Authentification successful!")
    return True

def api(server, command):
    logging.info("--> Starting access over api")
    serversFile = getRegisteredServers()
    result = None
    if server in serversFile:
        server = serversFile[server]
        logging.info("Server found! Connecting...")
        client = connect(server["ip"], server["port"])
        if client:
            if authenticate(client, server["key"]):
                sendMessage(client, command)
                result = receiveMessage(client)
                logging.info("--> Finish access over api successful!")
                client.close()
                return result

    logging.info("--> Finish access over api with error")
    return False
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", required=True, help="Name of satellite to send sync command(s)")
    parser.add_argument("--items", nargs="+", required=True, help="List items to sync")

    args = parser.parse_args()

    serversFile = getRegisteredServers()
    if args.name in serversFile:
        server = serversFile[args.name]
        logging.info("Server found! Connecting...")
        client = connect(server["ip"], server["port"])
        authenticate(client, server["key"])

        #for item in args.items:
        sendMessage(client, "ping")

        receiveMessage(client)

        logging.info("Finished!")
        client.close()
    

if __name__ == "__main__":
    main()

