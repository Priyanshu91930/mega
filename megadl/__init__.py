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
if sys.platform != "win32":  # type: ignore[comparison-overlap]
    try:
        import asyncio
        import uvloop
        # 1) Install uvloop as the event loop policy first.
        # 2) THEN create + set a loop, so pyrogram's import-time
        #    asyncio.get_event_loop() call (in sync.py) finds a valid loop.
        # Doing it the other way around doesn't work because uvloop.install()
        # replaces the entire policy, discarding any previously set loop.
        uvloop.install()
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
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

# Import modules AFTER CypherClient is created so their
# @CypherClient.on_message(...) decorators can register handlers.
from .modules import admin, auth, bonus, callbacks, generals, mega_dl, mega_up  # noqa: E402, F401
print(f"> Modules loaded successfully")
print(f"> Auth users: {CypherClient.auth_users} (empty = nobody can use bot!)")