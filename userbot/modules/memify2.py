"""base by: @r4v4n4
created by: @A_Dark_Princ3"""

from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon import events
from io import BytesIO
from PIL import Image
import asyncio
import time
from datetime import datetime
from telethon.tl.types import DocumentAttributeVideo
from userbot.utils import progress, humanbytes, time_formatter
import datetime
from collections import defaultdict
import math
import os
import requests
import zipfile
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import (
DocumentAttributeFilename,
DocumentAttributeSticker,
InputMediaUploadedDocument,
InputPeerNotifySettings,
InputStickerSetID,
InputStickerSetShortName,
MessageMediaPhoto
)
from userbot import bot, TEMP_DOWNLOAD_DIRECTORY
from userbot.events import register

thumb_image_path = TEMP_DOWNLOAD_DIRECTORY + "/thumb_image.jpg"


@register(outgoing=True, pattern=r"^\.mem(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
       await event.edit("`Usage:Nibba reply to an image with .mem And Text `")
       return
    reply_message = await event.get_reply_message()
    if not reply_message.media:
       await event.edit("```reply to a image/sticker/gif```")
       return
    chat = "@MemeCreatorBot"
    sender = reply_message.sender
    file_ext_ns_ion = "@memeimg.png"
    uploaded_gif = None
    if reply_message.sender.bot:
       await event.edit("```Reply to actual users message LOL.```")
       return
    else:
       await event.edit("```Transfiguration Time! Mwahaha memifying this image! (」ﾟﾛﾟ)｣ ```")
    file = await bot.download_file(reply_message.media)
    async with bot.conversation("@MemeCreatorBot") as bot_conv:
          try:
            memeVar = event.pattern_match.group(1)
            await silently_send_message(bot_conv, "/start")
            await asyncio.sleep(1)
            await silently_send_message(bot_conv, memeVar)
            await bot.send_file(chat, reply_message.media)
            response = await bot_conv.get_response()
          except YouBlockedUserError:
              await event.reply("```Please unblock @MemeCreatorBot and try again```")
              return
          if response.text.startswith("Forward"):
              await event.edit("```can you kindly disable your forward privacy settings for good nibba?```")
          if "Send" in response.text:
            await event.edit("```🤨 NANI?! This is not an image! This will take sum tym to convert to image owo 🧐```")
            thumb = None
            if os.path.exists(thumb_image_path):
                thumb = thumb_image_path
            input_str = event.pattern_match.group(1)
            if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
                os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
            if event.reply_to_msg_id:
                file_name = "meme.png"
                reply_message = await event.get_reply_message()
                to_download_directory = TEMP_DOWNLOAD_DIRECTORY
                downloaded_file_name = os.path.join(to_download_directory, file_name)
                downloaded_file_name = await bot.download_media(
                    reply_message,
                    downloaded_file_name,
                    )
                if os.path.exists(downloaded_file_name):
                    await bot.send_file(
                        chat,
                        downloaded_file_name,
                        force_document=False,
                        supports_streaming=False,
                        allow_cache=False,
                        thumb=thumb,
                        )
                    os.remove(downloaded_file_name)
                else:
                    await event.edit("File Not Found {}".format(input_str))
            response = await bot_conv.get_response()
            the_download_directory = TEMP_DOWNLOAD_DIRECTORY
            files_name = "memes.webp"
            download_file_name = os.path.join(the_download_directory, files_name)
            await bot.download_media(
                response.media,
                download_file_name,
                )
            requires_file_name = TEMP_DOWNLOAD_DIRECTORY + "memes.webp"
            await bot.send_file(  # pylint:disable=E0602
                event.chat_id,
                requires_file_name,
                supports_streaming=False,
                caption="memetime",
                # Courtesy: @A_Dark_Princ3
            )
            await event.delete()
            msg = await bot.send_message(event.chat_id, "Memeify Sucess !")
            await asyncio.sleep(4)
            msg.delete()
          elif not is_message_image(reply_message):
            await event.edit("```LOL WTF Are u Dumb or I'M Dumb```")
            return
          else:
               await bot.send_file(event.chat_id, response.media)

def is_message_image(message):
    if message.media:
        if isinstance(message.media, MessageMediaPhoto):
            return True
        if message.media.document:
            if message.media.document.mime_type.split("/")[0] == "image":
                return True
        return False
    return False

async def silently_send_message(conv, text):
    await conv.send_message(text)
    response = await conv.get_response()
    await conv.mark_read(message=response)
    return response

