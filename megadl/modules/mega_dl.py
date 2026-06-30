# Copyright (c) 2021 - Present partiallywritten
# Author: https://github.com/partiallywritten
# Project: https://github.com/partiallywritten/Mega.nz-Bot
# Description: Handle mega.nz download function


import re
import logging
from os import path, makedirs

from pyrogram import filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from megadl import CypherClient
from megadl.lib.megatools import MegaTools


@CypherClient.on_message(
    filters.regex(r"(https?:\/\/mega\.nz\/(file|folder|#)?.+)|(\/Root\/?.+)")
)
@CypherClient.run_checks
async def dl_from(client: CypherClient, msg: Message):
    # Push info to temp db
    _mid = msg.id
    _usr = msg.from_user.id
    client.glob_tmp[_usr] = [msg.text, f"{client.dl_loc}/{_usr}"]
    await msg.reply(
        "**Select what you want to do 🤗**",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Download 💾", callback_data=f"dwn_mg-{_mid}")],
                [InlineKeyboardButton("Info ℹ️", callback_data=f"info_mg-{_mid}")],
                [InlineKeyboardButton("Cancel ❌", callback_data=f"cancelqcb-{_usr}")],
            ]
        ),
    )


prv_rgx = r"(\/Root\/?.+)"


@CypherClient.on_callback_query(filters.regex(r"dwn_mg?.+"))
@CypherClient.run_checks
async def dl_from_cb(client: CypherClient, query: CallbackQuery):
    # Access saved info
    _mid = int(query.data.split("-")[1])
    qcid = query.message.chat.id
    qusr = query.from_user.id
    dtmp = client.glob_tmp.get(qusr)
    url = dtmp[0]
    dlid = dtmp[1]

    # weird workaround to add support for private mode
    conf = None
    if client.is_public:
        udoc = await client.database.is_there(qusr, True)
        if not udoc and re.match(prv_rgx, url):
            return await query.edit_message_text(
                "`You must be logged in first to download this file 😑`"
            )
        if udoc:
            email = client.cipher.decrypt(udoc["email"]).decode()
            password = client.cipher.decrypt(udoc["password"]).decode()
            proxy = f"--proxy {udoc['proxy']}" if udoc["proxy"] else ""
            conf = f"--username {email} --password {password} {proxy}"

    # Create unique download folder
    if not path.isdir(dlid):
        makedirs(dlid)

    # Download the file/folder
    resp = await query.edit_message_text(
        "`Your download is starting 📥...`", reply_markup=None
    )

    cli = MegaTools(client, conf)

    # If it is a public folder link, resolve files and download them one by one
    if "folder" in url or "#F!" in url:
        try:
            await resp.edit("`Fetching folder contents... 🔎`")
            files = await cli.get_folder_files(url)
        except Exception as e:
            logging.error(f"Failed to fetch folder files: {e}")
            return await resp.edit(f"`Failed to fetch folder: {e}`")

        if not files:
            return await resp.edit("`No files found or folder is empty/invalid.`")

        await resp.edit(f"`Found {len(files)} files. Downloading and uploading sequentially...`")

        success_count = 0
        failed_files = []

        for idx, f in enumerate(files, 1):
            try:
                # Update status
                await resp.edit(f"`[{idx}/{len(files)}] Downloading: {f['name']}`")
                
                # Download single file using choose-files
                single_list = await cli.download_file_from_folder(
                    url,
                    f['name'],
                    qusr,
                    qcid,
                    resp.id,
                    path=dlid,
                )
                
                if single_list:
                    # Upload single file immediately!
                    await resp.edit(f"`[{idx}/{len(files)}] Uploading: {f['name']}`")
                    await client.send_files(
                        single_list,
                        qcid,
                        resp.id,
                        reply_to_message_id=_mid,
                        caption=f"**File:** `{f['name']}`\n\n**Join @NexaBotsUpdates ❤️**",
                    )
                    success_count += 1
                # Clean up local folder for the next file
                await client.full_cleanup(dlid, qusr)
            except Exception as e:
                failed_files.append(f['name'])
                logging.warning(f"Failed to download/upload {f['name']}: {e}")
                # Clean up local folder anyway
                await client.full_cleanup(dlid, qusr)

        # Final status message
        status_text = f"**Folder Processed!** ✅\n\n**Success:** `{success_count}/{len(files)}` files"
        if failed_files:
            status_text += f"\n**Failed/Blocked:** `{len(failed_files)}` files"
        await resp.edit(status_text)
        return

    # Default direct flow for single files
    f_list = None
    try:
        f_list = await cli.download(
            url,
            qusr,
            qcid,
            resp.id,
            path=dlid,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Cancel ❌", callback_data=f"cancelqcb-{qusr}")],
                ]
            ),
        )
    except Exception as e:
        from megadl.helpers.files import listfiles
        f_list = listfiles(dlid)
        if not f_list:
            raise e
        else:
            logging.warning(f"Download partially failed: {e}")
            await resp.edit(f"`Download partially completed. Error: {e.args[0] if e.args else e}`\n`Uploading successfully downloaded files...`")

    if not f_list:
        return

    await query.edit_message_text("`Successfully downloaded the content 🥳`")
    # update download count
    if client.database:
        await client.database.plus_fl_count(qusr, downloads=len(f_list))
    # Send file(s) to the user
    await resp.edit("`Trying to upload now 📤...`")
    await client.send_files(
        f_list,
        qcid,
        resp.id,
        reply_to_message_id=_mid,
        caption=f"**Join @NexaBotsUpdates ❤️**",
    )
    await client.full_cleanup(dlid, qusr)
    await resp.delete()
