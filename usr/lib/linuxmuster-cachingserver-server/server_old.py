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

logging.basicConfig(filename='/var/log/linuxmuster/cachingserver/server.log',format='%(levelname)s: %(asctime)s %(message)s', level=logging.DEBUG)

def error(conn, addr, msg):
    logging.error(msg)
    conn.close()
    logging.error(f"Connection with {addr} terminated!")

def sendMessage(conn, msg):
    if len(msg) > 40:
        logging.debug(f"[{conn.getpeername()[0]}] Send message '" + msg[:40].replace('\n', '') + "...'")
    else:
        logging.debug(f"[{conn.getpeername()[0]}] Send message '{msg}'")
    conn.send(msg.encode("utf-8"))

def sendData(conn, data, part=None):
    if part != None:
        logging.debug(f"[{conn.getpeername()[0]}] [{part}] Send data...")
    else:
        logging.debug(f"[{conn.getpeername()[0]}] Send data...")
    conn.send(data)

def getConfig():
    return json.load(open("/etc/linuxmuster-cachingserver/config.json", "r"))

def receiveMessage(conn):
    try:
        message = conn.recv(1024).decode()
    except:
        return None
    logging.debug(f"[{conn.getpeername()[0]}] Receive message '{message}'")
    return message

def getRegisteredServers():
    file = open("/var/lib/linuxmuster-cachingserver/servers.json", "r")
    json_result = json.load(file)
    file.close()
    return json_result

def getActions():
    file = open("/etc/linuxmuster-cachingserver/actions.json", "r")
    json_result = json.load(file)
    file.close()
    return json_result

def checkServer(serversFile, ip):
    for server in serversFile:
        if ip == serversFile[server]["ip"]:
            return serversFile[server]
    return False

def sendFile(conn, filename):
    sendMessage(conn, "file")
    if receiveMessage(conn) != "ok":
        return False
    file = open(filename, "rb")
    data = file.read()
    file.close()
    filesize = os.stat(filename).st_size
    logging.info(f"[{conn.getpeername()[0]}] Sending file {filename} with {filesize} bytes")
    sendMessage(conn, filename + ";" + str(filesize))
    if receiveMessage(conn) != "ok":
        return False
    if filesize > 0:
        fileparts = (int(filesize / 1024) + 1)
        logging.debug(f"[{conn.getpeername()[0]}] Sending file in {fileparts} parts")
        sendData(conn, data)
    if receiveMessage(conn) != "ok":
        return False
    logging.info(f"[{conn.getpeername()[0]}] File {filename} send successfully!")
    return True

def sendFiles(conn, pattern, delete=False, end=True):
    returnVal = True
    for filename in glob.glob(pattern, recursive=True):
        if os.path.isfile(filename):
            if not sendFile(conn, filename):
                returnVal = False
            if delete:
                os.remove(filename)
    
    if end:
        sendMessage(conn, "end")
        logging.info(f"[{conn.getpeername()[0]}] All files are send successfully!")

    return returnVal

def main():
    ip = getConfig()["ip"]
    port = getConfig()["port"]
    logging.info(f"Starting Cachingserver-Server on {ip}:{port}")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ip, port))
    server.listen()

    serversFile = getRegisteredServers()

    logging.info("Server started!")

    actions = getActions()

    while True:
        conn, addr = server.accept()
        logging.debug(f"New connection from {addr}")

        serverCheck = checkServer(serversFile, addr[0])

        if not serverCheck:
            error(conn, addr, f"[{addr[0]}] Server not registered!")
            continue

        message = receiveMessage(conn)
        if message == None:
            error(conn, addr, f"[{addr[0]}] Invalid message reveived!")
            continue

        message = message.split(" ", 1)
        if message[0] == "auth":
            if message[1] == serverCheck["key"]:
                logging.info(f"[{addr[0]}] Authenification successful!")
                sendMessage(conn, "hello")
            else:
                error(conn, addr, f"[{addr[0]}] Authenification failed! Reset connection!")
                continue
        
        while True:
            message = receiveMessage(conn).split(" ", 1)
            if message == None:
                error(conn, addr, f"[{addr[0]}] Invalid message reveived!")
                continue

            if message[0] == "get":
                if message[1] in actions:
                    sendMessage(conn, "ok")
                    logging.debug(f"[{addr[0]}] Action is valid!")

                    # check for prehook
                    if receiveMessage(conn) == "prehook?":
                        prehook = actions[message[1]]["prehook"] if "prehook" in actions[message[1]] else "no"
                        sendMessage(conn, prehook)
                        if receiveMessage(conn) != "done":
                            logging.error(f"[{addr[0]}] Client said prehook failed!")
                        else:
                            logging.info(f"[{addr[0]}] Client said prehook was successful!")
                    else:
                        error(conn, addr, f"[{addr[0]}] Client send invalid prehook command!")
                        continue

                    if receiveMessage(conn) != "start":
                        error(conn, addr, f"[{addr[0]}] Client send invalid start command!")
                        continue
                    
                    pattern = actions[message[1]]["pattern"].replace("#school#", serverCheck["school"])
                    delete = actions[message[1]]["delete"] if "delete" in actions[message[1]] else False

                    if ";" in pattern:
                        pat_split = pattern.split(";")
                        count = 1
                        for pat in pat_split:
                            if count == len(pat_split):
                                if not sendFiles(conn, pat, delete):
                                    error(conn, addr, f"[{addr[0]}] Error while sending file to client!")
                                    continue
                            else:
                                if not sendFiles(conn, pat, delete, False):
                                    error(conn, addr, f"[{addr[0]}] Error while sending file to client!")
                                    continue

                            count+= 1

                    else:
                        if not sendFiles(conn, pattern, delete):
                            error(conn, addr, f"[{addr[0]}] Error while sending file to client!")
                            continue

                    # check for posthook
                    if receiveMessage(conn) == "posthook?":
                        posthook = actions[message[1]]["posthook"] if "posthook" in actions[message[1]] else "no"
                        sendMessage(conn, posthook)
                        if receiveMessage(conn) != "done":
                            logging.error(f"[{addr[0]}] Client said posthook failed!")
                        else:
                            logging.info(f"[{addr[0]}] Client said posthook was successful!")
                    else:
                        error(conn, addr, f"[{addr[0]}] Client send invalid posthook command!")
                        continue

                else:
                    sendMessage(conn, "invalid")
                    error(conn, addr, f"[{addr[0]}] Client send invalid action!")
                    continue
            elif message[0] == "bye":
                logging.info(f"[{conn.getpeername()[0]}] Client disconnected!")
                break

        conn.close()

if __name__ == "__main__":
    logging.info("======= STARTED =======")
    try:
        main()
    except UnicodeDecodeError:
        logging.info("======= INVALID CONNECTION - RESTARTED =======")
        main()
    except KeyboardInterrupt:
        logging.info("======= STOPPED (by user) =======")
        exit(0)
    except Exception as e:
        logging.info("======= STOPPED (by error) =======")
        logging.error(e)
        exit(1)