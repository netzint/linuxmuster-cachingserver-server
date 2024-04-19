#!/usr/bin/env python3
#
# by lukas.spitznagel@netzint.de
#

import os

from rsync-hook-handler import RSyncHookHandler

RSyncHookHandler(RSyncHookHandler.HANDLER_TYPE_PRE, RSyncHookHandler.HANDLER_DIRECTION_UPLOAD, os.environ)