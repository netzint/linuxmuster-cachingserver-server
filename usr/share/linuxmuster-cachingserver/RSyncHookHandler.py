#!/usr/bin/env python3
#
# by lukas.spitznagel@netzint.de
#

import logging
import json

logging.basicConfig(filename='/var/log/linuxmuster/cachingserver/rsync-server.log',format='%(levelname)s: %(asctime)s %(message)s', level=logging.DEBUG)

class RSyncHookHandler:

    HANDLER_TYPE_PRE = "PRE"
    HANDLER_TYPE_POST = "POST"

    HANDLER_DIRECTION_UPLOAD = "UPLOAD"
    HANDLER_DIRECTION_DOWNLOAD = "DOWNLOAD"

    def __init__(self, handler_type:str, handler_direction:str, environment:list):
        self.handler_type = handler_type
        self.handler_direction = handler_direction
        self.environment = environment

        self.handle()

    def handle(self):
        if self.handler_type == self.HANDLER_TYPE_PRE:
            logging.info(f"[{self.environment['RSYNC_PID']}] New connection from {self.environment['RSYNC_HOST_ADDR']}...")
            if self.handler_direction == self.HANDLER_DIRECTION_DOWNLOAD:
                self.__handle_pre_download()
            elif self.handler_direction == self.HANDLER_DIRECTION_UPLOAD:
                self.__handle_pre_upload()
        elif self.handler_type == self.HANDLER_TYPE_POST:
            if self.handler_direction == self.HANDLER_DIRECTION_DOWNLOAD:
                self.__handle_post_download()
            elif self.handler_direction == self.HANDLER_DIRECTION_UPLOAD:
                self.__handle_post_upload()
            logging.info(f"[{self.environment['RSYNC_PID']}] Connection with {self.environment['RSYNC_HOST_ADDR']} closed...")

    def __handle_pre_download(self):
        """
        {'RSYNC_MODULE_PATH': '/srv/linbo', 'RSYNC_ARG0': 'rsyncd', 'RSYNC_HOST_ADDR': '10.0.0.50', 'RSYNC_ARG1': '--server', 'RSYNC_ARG2': '--sender', 'RSYNC_ARG3': '-vlogDtprce.iLsfxCIvu', 'RSYNC_ARG4': '--ignore
        -missing-args', 'RSYNC_ARG5': '.', 'SYSTEMD_EXEC_PID': '3889683', 'RSYNC_ARG6': 'boot/grub/grub.cfg', 'RSYNC_HOST_NAME': 'UNKNOWN', 'RSYNC_ARG7': 'boot/grub/win10-generic-bios.cfg', 'RSYNC_USER_NAME': 'cache01', 'JOURNAL_STREAM': '8:737
        42884', 'RSYNC_REQUEST': 'cachingserver-linbo/boot/grub/*.cfg', 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin', 'INVOCATION_ID': 'a6536957309a4beb992809ba42b6fdaf', 'LANG': 'en_US.UTF-8', 'RSYNC_MODULE_
        NAME': 'cachingserver-linbo', 'PWD': '/', 'RSYNC_PID': '3894232'}
        """
        logging.info(f"[{self.environment['RSYNC_PID']}] [PRE] Request '{self.environment['RSYNC_REQUEST']}' as user '{self.environment['RSYNC_USER_NAME']}'")

        if self.environment['RSYNC_REQUEST'] == "cachingserver-linuxmuster-cachingserver/" + self.environment['RSYNC_USER_NAME'] + "_images.json":
            logging.info(f"[{self.environment['RSYNC_PID']}]  -> running prehook to create image database file for '{self.environment['RSYNC_USER_NAME']}'")
            server = json.load(open("/var/lib/linuxmuster-cachingserver/servers.json"))[self.environment['RSYNC_USER_NAME']]
            cache_server_file = open("/var/lib/linuxmuster-cachingserver/" + self.environment['RSYNC_USER_NAME'] + "_images.json", "w")
            json.dump(server["images"], cache_server_file, indent=4)
            cache_server_file.close()

    def __handle_post_download(self):
        """
        {'RSYNC_MODULE_PATH': '/var/lib/linuxmuster-cachingserver', 'RSYNC_HOST_ADDR': '10.0.0.50', 'RSYNC_RAW_STATUS': '0', 'RSYNC_EXIT_STATUS': '0', 'SYSTEMD_EXEC_PID': '3896324', 'RSYNC_HOST_NAME': 'UNKNOWN', 'R
        SYNC_USER_NAME': 'cache01', 'JOURNAL_STREAM': '8:73840280', 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin', 'INVOCATION_ID': '2bca4e0e91ec4c61a5e4ecfaee1c1ac4', 'LANG': 'en_US.UTF-8', 'RSYNC_MODULE_NAME
        ': 'cachingserver-linuxmuster-cachingserver', 'PWD': '/', 'RSYNC_PID': '3896970'}
        """
        pass

    def __handle_pre_upload(self):
        pass

    def __handle_post_upload(self):
        pass