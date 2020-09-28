import os
import shlex
import asyncio
from os.path import basename
from typing import Optional, Tuple
from userbot import TEMP_DOWNLOAD_DIRECTORY
from userbot.utils import take_screen_shot, runcmd, progress

# For using gif , animated stickers and videos in some parts , this
# function takes  take a screenshot and stores ported from userge


async def take_screen_shot(video_file: str, duration: int, path: str = '') -> Optional[str]:
    print(
        '[[[Extracting a frame from %s ||| Video duration => %s]]]',
        video_file,
        duration)
    ttl = duration // 2
    thumb_image_path = path or os.path.join(
        "./temp/", f"{basename(video_file)}.jpg")
    command = f"ffmpeg -ss {ttl} -i '{video_file}' -vframes 1 '{thumb_image_path}'"
    err = (await runcmd(command))[1]
    if err:
        print(err)
    return thumb_image_path if os.path.exists(thumb_image_path) else None

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
        stkr_file = os.path.join(TEMP_DOWNLOAD_DIRECTORY, "stkr.png")
        os.rename(dls_loc, stkr_file)
        if not os.path.lexists(stkr_file):
            await event.edit("```Sticker not found...```")
            return
        dls_loc = stkr_file
    elif replied.animation or replied.video:
        await event.edit("`Converting Media To Image ...`")
        jpg_file = os.path.join(TEMP_DOWNLOAD_DIRECTORY, "image.jpg")
        await take_screen_shot(dls_loc, 0, jpg_file)
        os.remove(dls_loc)
        if not os.path.lexists(jpg_file):
            await event.edit("This Gif is Gey (｡ì _ í｡), Task Failed Successfully !")
            return
        dls_loc = jpg_file
    await event.edit("`Almost Done ...`")
    return dls_loc
    await event.delete()

# executing of terminal commands


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(*args,
                                                   stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    return (stdout.decode('utf-8', 'replace').strip(),
            stderr.decode('utf-8', 'replace').strip(),
            process.returncode,
            process.pid)
