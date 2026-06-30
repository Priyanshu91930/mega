# Copyright (c) 2021 - Present partiallywritten
# Author: https://github.com/partiallywritten
# Project: https://github.com/partiallywritten/Mega.nz-Bot
# Description: __init__.py

import os
import sys
import logging

# start msg
print("Mega.nz Bot - Cypher is starting...")

# uvloop integration for better asyncio performance
# only on Unix-like systems (not Windows)
if sys.platform != "win32":
    try:
        import asyncio
        import uvloop
        # Must create and set a loop BEFORE uvloop.install(), because uvloop's
        # get_event_loop() (used by pyrogram at import time) raises RuntimeError
        # on Python 3.10+ if no current event loop exists in the main thread.
        _loop = uvloop.new_event_loop()
        asyncio.set_event_loop(_loop)
        uvloop.install()
        print("> Using uvloop for better performance")
    except ImportError:
        pass

# loading config
from dotenv import load_dotenv
print("--------------------")
print("> Loading config")
if os.path.isfile('.env'):
    load_dotenv()
else:
    logging.warning("WARNING: No .env file found")

# client
from .helpers.cypher import MeganzClient
CypherClient: "MeganzClient" = MeganzClient()