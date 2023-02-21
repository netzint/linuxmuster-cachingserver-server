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
import glob
import os

logging.basicConfig(filename='/var/log/linuxmuster/cachingserver-server.log',format='%(levelname)s: %(asctime)s %(message)s', level=logging.DEBUG)

def error(conn, addr, msg):
    logging.error(msg)
    conn.close()
    logging.error(f"Connection with {addr} terminated!")

def sendMessage(conn, msg):
    conn.send(msg.encode("utf-8"))

def getConfig():
    return json.load(open("/etc/linuxmuster-cachingserver/config.json", "r"))

def receiveMessage(conn):
    message = conn.recv(1024).decode()
    logging.debug(f"[{conn.getpeername()[0]}] Receive command '{message}'")
    return message

def getRegisteredServers():
    return json.load(open("/var/lib/linuxmuster-cachingserver/servers.json", "r"))

def checkServer(serversFile, ip):
    for server in serversFile:
        if ip == serversFile[server]["ip"]:
            return serversFile[server]
    return False

def sendFile(conn, filename):
    logging.info(f"[{conn.getpeername()[0]}] Send file {filename}")
    sendMessage(conn, "file")
    if receiveMessage(conn) != "ok":
        return False
    file = open(filename, "r")
    data = file.read()
    sendMessage(conn, filename + ";" + str(len(data)))
    if receiveMessage(conn) != "ok":
        return False
    sendMessage(conn, data)
    if receiveMessage(conn) != "ok":
        return False
    logging.info(f"[{conn.getpeername()[0]}] File {filename} send successfully!")
    return True

def sendFiles(conn, pattern, delete=False):
    returnVal = True
    for filename in glob.glob(pattern, recursive=True):
        if os.path.isfile(filename):
            if not sendFile(conn, filename):
                returnVal = False
            if delete:
                os.remove(filename)
    sendMessage(conn, "end")
    logging.info(f"[{conn.getpeername()[0]}] All files are send successfully!")
    return returnVal

def main():
    ip = getConfig()["ip"]
    port = getConfig()["port"]
    logging.info(f"Starting Cachingserver-Server on {ip}:{port}")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen()

    serversFile = getRegisteredServers()

    logging.info("Server started!")

    actions = {
        "rsync-config": {
            "pattern": "/etc/rsyncd.conf"
        },
        "rsync-secret": {
            "pattern": "/etc/rsyncd.secrets"
        },
        "ssh-keys": {
            "pattern": "/root/.ssh/id_rsa*"
        },
        "linuxmuster-setup": {
            "pattern": "/var/lib/linuxmuster/setup.ini"
        },
        "linbo-start-conf": {
            "pattern": "/srv/linbo/start.conf.*"
        },
        "linbo-grub-conf": {
            "pattern": "/srv/linbo/boot/grub/*.cfg"
        },
        "linbo-image-reg": {
            "pattern": "/srv/linbo/images/*/*.reg"
        },
        "linbo-image-postsync": {
            "pattern": "/srv/linbo/images/*/*.postsync"
        },
        "linbo-image-prestart": {
            "pattern": "/srv/linbo/images/*/*.prestart"
        },
        "linbo-linbocmd": {
            "pattern": "/srv/linbo/linbocmd/*",
            "delete": True
        },
        "linuxmuster-devices": {
            "pattern": "/etc/linuxmuster/sophomorix/#school#/devices.csv"
        },
        "linbo-log": {
            "pattern": "/srv/linbo/log/*"
        },
        "dhcp": {
            "pattern": "/etc/dhcp/**/*"
        },
    }

    while True:
        conn, addr = server.accept()
        logging.debug(f"New connection from {addr}")

        serverCheck = checkServer(serversFile, addr[0])

        if not serverCheck:
            error(conn, addr, f"[{addr[0]}] Server not registered!")
            continue

        message = receiveMessage(conn).split(" ", 1)
        if message[0] == "auth":
            if message[1] == serverCheck["key"]:
                logging.info(f"[{addr[0]}] Authenification successful!")
                sendMessage(conn, "hello")
            else:
                error(conn, addr, f"[{addr[0]}] Authenification failed! Reset connection!")
                continue

        message = receiveMessage(conn).split(" ", 1)
        if message[0] == "get":
            if message[1] in actions:
                sendMessage(conn, "ok")
                if receiveMessage(conn) != "start":
                    error(conn, addr, f"[{addr[0]}] Client send invalid start command!")
                    continue
                
                pattern = actions[message[1]]["pattern"].replace("#school#", serverCheck["school"])
                delete = actions[message[1]]["delete"] if "delete" in actions[message[1]] else False

                if not sendFiles(conn, pattern, delete):
                    error(conn, addr, f"[{addr[0]}] Error while sending file to client!")
                    continue
            else:
                sendMessage(conn, "invalid")
                error(conn, addr, f"[{addr[0]}] Client send invalid action!")
                continue

        conn.close()
    server.close()



if __name__ == "__main__":
    logging.info("======= STARTED =======")
    try:
        main()
    except KeyboardInterrupt:
        logging.info("======= STOPPED (by user) =======")
        exit(0)
    except Exception as e:
        logging.info("======= STOPPED (by error) =======")
        logging.error(e)
        exit(1)