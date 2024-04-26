#!/usr/bin/env python3
#
# by lukas.spitznagel@netzint.de
#

import os
import sys

sys.path.append("/usr/share/linuxmuster-cachingserver")
from RSyncHookHandler import RSyncHookHandler

RSyncHookHandler(RSyncHookHandler.HANDLER_TYPE_POST, RSyncHookHandler.HANDLER_DIRECTION_DOWNLOAD, dict(os.environ))