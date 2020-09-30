# Copyright (C) 2020 MoveAngel and MinaProject
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
# Multifunction memes
#
# Based code + improve from AdekMaulana and aidilaryanto

import asyncio
import io
import os
import random
import re
import textwrap
import time
from asyncio.exceptions import TimeoutError
from random import randint, uniform

from glitch_this import ImageGlitcher
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
from telethon import events, functions, types
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.types import DocumentAttributeFilename

from userbot import CMD_HELP, TEMP_DOWNLOAD_DIRECTORY, bot
from userbot.events import register
from userbot.utils import progress

Glitched = TEMP_DOWNLOAD_DIRECTORY + "glitch.gif"

@register(outgoing=True, pattern=r"^\.glit(?: |$)(.*)")
async def glitch(event):
    if not event.reply_to_msg_id:
        await event.edit("`I Wont Glitch A Ghost!`")
        return
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        await event.edit("`reply to a image/sticker`")
        return
    await event.edit("`Downloading Media..`")
    if reply_message.photo:
        glitch_file = await bot.download_media(
            reply_message,
            "glitch.png",
        )
    elif (
        DocumentAttributeFilename(file_name="AnimatedSticker.tgs")
        in reply_message.media.document.attributes
    ):
        await bot.download_media(
            reply_message,
            "anim.tgs",
        )
        os.system("lottie_convert.py anim.tgs anim.png")
        glitch_file = "anim.png"
    elif reply_message.video:
        video = await bot.download_media(
            reply_message,
            "glitch.mp4",
        )
        extractMetadata(createParser(video))
        os.system("ffmpeg -i glitch.mp4 -vframes 1 -an -s 480x360 -ss 1 glitch.png")
        glitch_file = "glitch.png"
    else:
        glitch_file = await bot.download_media(
            reply_message,
            "glitch.png",
        )
    try:
        value = int(event.pattern_match.group(1))
        if value > 8:
            raise ValueError
    except ValueError:
        value = 2
    await event.edit("```Glitching This Media..```")
    await asyncio.sleep(2)
    glitcher = ImageGlitcher()
    img = Image.open(glitch_file)
    glitch_img = glitcher.glitch_image(img, value, color_offset=True, gif=True)
    DURATION = 200
    LOOP = 0
    glitch_img[0].save(
        Glitched,
        format="GIF",
        append_images=glitch_img[1:],
        save_all=True,
        duration=DURATION,
        loop=LOOP,
    )
    await event.edit("`Uploading Glitched Media..`")
    c_time = time.time()
    nosave = await event.client.send_file(
        event.chat_id,
        Glitched,
        force_document=False,
        reply_to=event.reply_to_msg_id,
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(d, t, event, c_time, "[UPLOAD]")
        ),
    )
    await event.delete()
    os.remove(Glitched)
    await bot(
        functions.messages.SaveGifRequest(
            id=types.InputDocument(
                id=nosave.media.document.id,
                access_hash=nosave.media.document.access_hash,
                file_reference=nosave.media.document.file_reference,
            ),
            unsave=True,
        )
    )
    os.remove(glitch_file)
    os.system("rm -rf *.tgs")
    os.system("rm -rf *.mp4")
