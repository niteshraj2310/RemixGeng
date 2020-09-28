# Copyright (C) 2019 Adek Maulana
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
import asyncio
import hashlib
import os
from os.path import basename
import os.path
import re
import shlex
from os.path import basename
from typing import Optional
from typing import Tuple
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin
from telethon.tl.types import ChannelParticipantCreator
from telethon.tl.types import DocumentAttributeFilename
from userbot import bot
from userbot import LOGS
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator, DocumentAttributeFilename
import html
import random
from userbot import TEMP_DOWNLOAD_DIRECTORY
from userbot.utils import take_screen_shot, runcmd, progress


async def md5(fname: str) -> str:
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def humanbytes(size: int) -> str:
    if size is None or isinstance(size, str):
        return ""

    power = 2**10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


def time_formatter(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (((str(days) + " day(s), ") if days else "") +
           ((str(hours) + " hour(s), ") if hours else "") +
           ((str(minutes) + " minute(s), ") if minutes else "") +
           ((str(seconds) + " second(s), ") if seconds else ""))
    return tmp[:-2]


def human_to_bytes(size: str) -> int:
    units = {
        "M": 2**20,
        "MB": 2**20,
        "G": 2**30,
        "GB": 2**30,
        "T": 2**40,
        "TB": 2**40,
    }

    size = size.upper()
    if not re.match(r" ", size):
        size = re.sub(r"([KMGT])", r" \1", size)
    number, unit = [string.strip() for string in size.split()]
    return int(float(number) * units[unit])


async def is_admin(chat_id, user_id):
    req_jo = await bot(GetParticipantRequest(channel=chat_id, user_id=user_id))
    chat_participant = req_jo.participant
    return isinstance(chat_participant,
                      ChannelParticipantCreator) or isinstance(
                          chat_participant, ChannelParticipantAdmin)


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """ run command in terminal """
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


async def take_screen_shot(video_file: str, duration: int,
                           path: str = "") -> Optional[str]:
    """ take a screenshot """
    LOGS.info(
        "[[[Extracting a frame from %s ||| Video duration => %s]]]",
        video_file,
        duration,
    )
    ttl = duration // 2
    thumb_image_path = path or os.path.join("./temp/",
                                            f"{basename(video_file)}.jpg")
    command = f"ffmpeg -ss {ttl} -i '{video_file}' -vframes 1 '{thumb_image_path}'"
    err = (await runcmd(command))[1]
    if err:
        LOGS.error(err)
    return thumb_image_path if os.path.exists(thumb_image_path) else None


async def check_media(reply_message):
    if reply_message and reply_message.media:
        if reply_message.photo:
            data = reply_message.photo
        elif reply_message.document:
            if (
                DocumentAttributeFilename(file_name="AnimatedSticker.tgs")
                in reply_message.media.document.attributes
            ):
                return False
            if (
                reply_message.gif
                or reply_message.video
                or reply_message.audio
                or reply_message.voice
            ):
                return False
            data = reply_message.media.document
        else:
            return False
    else:
        return False

    if not data or data is None:
        return False
    else:
        return data

# For Downloading & Checking Media then Converting to Image.
# RETURNS an "Image".
"""Grabbed from USERGE"""



async def media_to_image(event):
    replied = event.reply_to_message
    if not (replied.photo or replied.sticker or replied.animation or replied.video):
        await event.edit("`Media Type Is Invalid ! See HELP.`")
        return
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
    await event.edit("`Ah Shit, Here We Go Again ...`")
    dls = await event.client.download_media(
        message=event.reply_to_message,
        file_name=TEMP_DOWNLOAD_DIRECTORY,
        progress=progress,
        progress_args=(event, "`Trying to Posses given content`")
    )
    dls_loc = os.path.join(TEMP_DOWNLOAD_DIRECTORY, os.path.basename(dls))
    if replied.sticker and replied.sticker.file_name.endswith(".tgs"):
        await event.edit("Converting Animated Sticker To Image...")
        png_file = os.path.join(TEMP_DOWNLOAD_DIRECTORY, "image.png")
        cmd = f"lottie_convert.py --frame 0 -if lottie -of png {dls_loc} {png_file}"
        stdout, stderr = (await runcmd(cmd))[:2]
        os.remove(dls_loc)
        if not os.path.lexists(png_file):
            await event.edit("This sticker is Gey, Task Failed Successfully ≧ω≦")
            raise Exception(stdout + stderr)
        dls_loc = png_file
    elif replied.sticker and replied.sticker.file_name.endswith(".webp"):
        stkr_file = os.path.join(TEMP_DOWNLOAD_DIRECTORY, , "stkr.png")
        os.rename(dls_loc, stkr_file)
        if not os.path.lexists(stkr_file):
            await event.edit("```Sticker not found...```")
            return
        dls_loc = stkr_file
    elif replied.animation or replied.video:
        await event.edit("`Converting Media To Image ...`")
        jpg_file = os.path.join(TEMP_DOWNLOAD_DIRECTORY, , "image.jpg")
        await take_screen_shot(dls_loc, 0, jpg_file)
        os.remove(dls_loc)
        if not os.path.lexists(jpg_file):
            await event.edit("This Gif is Gey (｡ì _ í｡), Task Failed Successfully !")
            return
        dls_loc = jpg_file
    await event.edit("`Almost Done ...`")
    return dls_loc
    await event.delete()
