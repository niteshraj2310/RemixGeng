# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
"""  Port From UniBorg to UserBot by @MoveAngel """

import os
from asyncio.exceptions import TimeoutError

from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError

from userbot import CMD_HELP, TEMP_DOWNLOAD_DIRECTORY, bot
from userbot.events import register


@register(outgoing=True, pattern=r"^\.q(?: |$)(.*)")
async def quotess(qotli):
    if qotli.fwd_from:
        return
    if not qotli.reply_to_msg_id:
        await qotli.edit("```Reply to any user message u NUB.```")
        return
    reply_message = await qotli.get_reply_message()
    if not reply_message.text:
        await qotli.edit("```Reply to text message BISH!```")
        return
    chat = "@QuotLyBot"
    reply_message.sender
    if reply_message.sender.bot:
        await qotli.edit("```Reply to actual NIBBA's  message.```")
        return
    try:
        await qotli.edit("`Making a Quote Plox Wait..`")
        async with bot.conversation(chat) as conv:
            try:
                response = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=1031952739)
                )
                msg = await bot.forward_messages(chat, reply_message)
                response = await response
                """don't spam notif"""
                await bot.send_read_acknowledge(conv.chat_id)
            except YouBlockedUserError:
                await qotli.reply("```Please unblock @QuotLyBot and try again```")
                return
            if response.text.startswith("Hi!"):
                await qotli.edit(
                    "```Abey Saley Can you kindly disable your forward privacy settings for good?```"
                )
            else:
                downloaded_file_name = await qotli.client.download_media(
                    response.media, TEMP_DOWNLOAD_DIRECTORY
                )
                await qotli.client.send_file(
                    qotli.chat_id, downloaded_file_name, reply_to=qotli.reply_to_msg_id
                )
                await qotli.delete()
                await bot.send_read_acknowledge(qotli.chat_id)
                """ - cleanup chat after completed - """
                await qotli.client.delete_messages(conv.chat_id, [msg.id, response.id])
                os.remove(downloaded_file_name)
    except TimeoutError:
        return await qotli.edit("`Error: `@QuotLyBot` is not responding!.`")


CMD_HELP.update({
    "quotly":
    "`.q`\
\nUsage: Enhance ur text to sticker."
})
