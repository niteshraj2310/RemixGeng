import asyncio
import logging
import os
import time
from datetime import datetime

from userbot import bot
from userbot import TEMP_DOWNLOAD_DIRECTORY
from userbot.events import register
from userbot.utils import progress
from PyDictionary import PyDictionary

@register(outgoing=True, pattern=r"^\.def(?: |$)(.*)")
async def _(event):
    word = event.pattern_match.group(1)
    dictionary = PyDictionary()
    words = dictionary.meaning(word)
    output = f"**Word :** `{word}`\n\n"
    try:
        for a, b in words.items():
            output += f"**{a}**:\n"
            for i in b:
                output += f">`{i}`\n"
        await event.edit(output)
    except Exception:
        await event.edit(f"Couldn't fetch meaning of {word}")

@register(outgoing=True, pattern=r"^\.imgs(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    await event.edit("```Converting.....```")
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
    if event.reply_to_msg_id:
        filename = "stkr.jpg"
        file_name = filename
        reply_message = await event.get_reply_message()
        to_download_directory = TEMP_DOWNLOAD_DIRECTORY
        downloaded_file_name = os.path.join(to_download_directory, file_name)
        downloaded_file_name = await bot.download_media(
            reply_message, downloaded_file_name)
        if os.path.exists(downloaded_file_name):
            picc = await bot.send_file(
                event.chat_id,
                downloaded_file_name,
                force_document=False,
                reply_to=reply_to_id,
            )
            os.remove(downloaded_file_name)
        else:
            await event.edit("```Ooof i can't handel dat```")

        await event.delete()


@register(outgoing=True, pattern=r"^\.stik(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    await event.edit("```Converting.....```")
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
    if event.reply_to_msg_id:
        filename = "kek.webp"
        file_name = filename
        reply_message = await event.get_reply_message()
        to_download_directory = TEMP_DOWNLOAD_DIRECTORY
        downloaded_file_name = os.path.join(to_download_directory, file_name)
        downloaded_file_name = await bot.download_media(
            reply_message, downloaded_file_name)
        if os.path.exists(downloaded_file_name):
            picc = await bot.send_file(
                event.chat_id,
                downloaded_file_name,
                force_document=False,
                reply_to=reply_to_id,
            )
            os.remove(downloaded_file_name)
        else:
            await event.edit("```Ooff i can't Handel Dat```")

        await event.delete()


@register(outgoing=True, pattern=r"^\.tft(?: |$)(.*)")
async def get(event):
    name = event.text[5:]
    if name is None:
        await event.edit("`reply correctly u DUMB`")
        return
    m = await event.get_reply_message()
    if m.text:
        with open(name, "w") as f:
            f.write(m.message)
        await event.delete()
        await bot.send_file(event.chat_id, name, force_document=True)
        os.remove(name)


@register(outgoing=True, pattern=r"^\.nfc(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await event.edit("```Reply to any media file LOL.```")
        return
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        await event.edit("reply to media file")
        return
    input_str = event.pattern_match.group(1)
    if input_str is None:
        await event.edit("`U DUMB DUDE`")
        return
    if input_str in ["mp3", "voice"]:
        await event.edit("`converting...`")
    else:
        await event.edit("try `.nfc voice` or`.nfc mp3`")
        return
    try:
        start = datetime.now()
        c_time = time.time()
        downloaded_file_name = await bot.download_media(
            reply_message,
            TEMP_DOWNLOAD_DIRECTORY,
            progress_callback=lambda d, t: asyncio.get_event_loop().
            create_task(progress(d, t, event, c_time, "trying to download")),
        )
    except Exception as e:  # pylint:disable=C0103,W0703
        await event.edit(str(e))
    else:
        end = datetime.now()
        ms = (end - start).seconds
        await event.edit("Downloaded to `{}` in {} seconds.".format(
            downloaded_file_name, ms))
        new_required_file_name = ""
        new_required_file_caption = ""
        command_to_run = []
        voice_note = False
        supports_streaming = False
        if input_str == "voice":
            new_required_file_caption = "voice_" + str(round(
                time.time())) + ".opus"
            new_required_file_name = (TEMP_DOWNLOAD_DIRECTORY + "/" +
                                      new_required_file_caption)
            command_to_run = [
                "ffmpeg",
                "-i",
                downloaded_file_name,
                "-map",
                "0:a",
                "-codec:a",
                "libopus",
                "-b:a",
                "100k",
                "-vbr",
                "on",
                new_required_file_name,
            ]
            voice_note = True
            supports_streaming = True
        elif input_str == "mp3":
            new_required_file_caption = "mp3_" + str(round(
                time.time())) + ".mp3"
            new_required_file_name = (TEMP_DOWNLOAD_DIRECTORY + "/" +
                                      new_required_file_caption)
            command_to_run = [
                "ffmpeg",
                "-i",
                downloaded_file_name,
                "-vn",
                new_required_file_name,
            ]
            voice_note = False
            supports_streaming = True
        else:
            await event.edit("not supported")
            os.remove(downloaded_file_name)
            return
        logging.info(command_to_run)
        # TODO: re-write create_subprocess_exec 😉
        process = await asyncio.create_subprocess_exec(
            *command_to_run,
            # stdout must a pipe to be accessible as process.stdout
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # Wait for the subprocess to finish
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
        os.remove(downloaded_file_name)
        if os.path.exists(new_required_file_name):
            end_two = datetime.now()
            force_document = False
            await bot.send_file(
                entity=event.chat_id,
                file=new_required_file_name,
                allow_cache=False,
                silent=True,
                force_document=force_document,
                voice_note=voice_note,
                supports_streaming=supports_streaming,
                progress_callback=lambda d, t: asyncio.get_event_loop().
                create_task(progress(d, t, event, c_time, "trying to upload")),
            )
            (end_two - end).seconds
            os.remove(new_required_file_name)
            await event.delete()
