# Copyright (c) 2021 - Present partiallywritten
# Author: https://github.com/partiallywritten
# Project: https://github.com/partiallywritten/Mega.nz-Bot
# Description: __main__.py

import asyncio

from pyrogram import idle

from . import CypherClient


async def run_bot():
    # Custom pyrogram client
    print("> Starting Client")
    await CypherClient.start()  # our async override sends the update message
    print("--------------------")
    await idle()


# Run the bot
if __name__ == "__main__":
    asyncio.run(run_bot())
