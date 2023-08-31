#!/usr/bin/env python3

#########################################################
# 
# by Netzint GmbH 2023
# Lukas Spitznagel (lukas.spitznagel@netzint.de)
# 
#########################################################

import logging
import time

from modules.sockethelper import SocketHepler

logging.basicConfig(filename='/var/log/linuxmuster/cachingserver/server.log',format='%(levelname)s: %(asctime)s %(message)s', level=logging.DEBUG)

def main():
    socket = SocketHepler("0.0.0.0", 4455)
    socket.setAuthfile("/var/lib/linuxmuster-cachingserver/servers.json")
    socket.start()
    socket.waitForClient()

if __name__ == "__main__":
    logging.info("======= STARTED =======")
    try:
        main()
    except OSError:
        logging.error("Server address is already in use. Wait for 10 seconds...")
        time.sleep(10)
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        logging.info("======= STOPPED =======")
