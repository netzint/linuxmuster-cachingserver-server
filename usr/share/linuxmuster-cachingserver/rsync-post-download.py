#!/usr/bin/env python3
#
# by lukas.spitznagel@netzint.de
#

import os

from rsync-hook-handler import RSyncHookHandler

RSyncHookHandler(RSyncHookHandler.HANDLER_TYPE_POST, RSyncHookHandler.HANDLER_DIRECTION_DOWNLOAD, os.environ)