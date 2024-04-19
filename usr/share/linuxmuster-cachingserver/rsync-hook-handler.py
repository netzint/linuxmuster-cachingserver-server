#!/usr/bin/env python3
#
# by lukas.spitznagel@netzint.de
#

import logging

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
        if self.handler_type == HANDLER_TYPE_PRE:
            logging.info(f"New connection from {self.environment['RSYNC_HOST_ADDR']}...")
            if self.handler_direction == HANDLER_DIRECTION_DOWNLOAD:
                self.__handle_pre_download()
            else if self.handler_direction == HANDLER_DIRECTION_UPLOAD:
                self.__handle_pre_upload()
        else if self.handler_type == HANDLER_TYPE_POST:
            if self.handler_direction == HANDLER_DIRECTION_DOWNLOAD:
                self.__handle_post_download()
            else if self.handler_direction == HANDLER_DIRECTION_UPLOAD:
                self.__handle_post_upload()
            logging.info(f"Connection with {self.environment['RSYNC_HOST_ADDR']} closed...")

    def __handle_pre_download(self):
        pass

    def __handle_post_download(self):
        pass

    def __handle_pre_upload(self):
        pass

    def __handle_post_upload(self):
        pass