# Copyright (C) 2020 Aidil Aryanto.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
# Vsong ported by AnggaR69S
# All rights reserved.

import glob
import os
import asyncio
import time
from asyncio.exceptions import TimeoutError
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from userbot import bot, CMD_HELP, lastfm, LASTFM_USERNAME
from telethon.tl.types import DocumentAttributeVideo
from pylast import User
from selenium import webdriver

from userbot import (
    GOOGLE_CHROME_BIN)
from userbot.events import register
from userbot.utils import progress


async def getmusicvideo(cat):
    video_link = ""
    search = cat
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--test-type")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = GOOGLE_CHROME_BIN
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get("https://www.youtube.com/results?search_query=" + search)
    user_data = driver.find_elements_by_xpath('//*[@id="video-title"]')
    for i in user_data:
        video_link = i.get_attribute("href")
        break
    command = 'youtube-dl -f "[filesize<50M]" --merge-output-format mp4 ' + video_link
    os.system(command)


@register(outgoing=True, pattern=r"^\.songn (?:(now)|(.*) - (.*))")
async def _(event):
    if event.fwd_from:
        return
    if event.pattern_match.group(1) == "now":
        playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
        if playing is None:
            return await event.edit(
                "`Error: No current scrobble found.`"
            )
        artist = playing.get_artist()
        song = playing.get_title()
    else:
        artist = event.pattern_match.group(2)
        song = event.pattern_match.group(3)
    track = str(artist) + " - " + str(song)
    chat = "@WooMaiBot"
    link = f"/netease {track}"
    await event.edit("`Searching...`")
    try:
        async with bot.conversation(chat) as conv:
            await asyncio.sleep(2)
            await event.edit("`Downloading...Please wait`")
            try:
                msg = await conv.send_message(link)
                response = await conv.get_response()
                respond = await conv.get_response()
                """- don't spam notif -"""
                await bot.send_read_acknowledge(conv.chat_id)
            except YouBlockedUserError:
                await event.reply("```Please unblock @WooMaiBot and try again```")
                return
            await event.edit("`Sending Your Music...`")
            await asyncio.sleep(3)
            await bot.send_file(event.chat_id, respond)
        await event.client.delete_messages(
            conv.chat_id, [msg.id, response.id, respond.id]
        )
        await event.delete()
    except TimeoutError:
        return await event.edit("`Error: `@WooMaiBot` is not responding!.`")


@register(outgoing=True, pattern=r"^\.songf (?:(now)|(.*) - (.*))")
async def _(event):
    if event.fwd_from:
        return
    if event.pattern_match.group(1) == "now":
        playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
        if playing is None:
            return await event.edit(
                "`Error: No scrobbling data found.`"
            )
        artist = playing.get_artist()
        song = playing.get_title()
    else:
        artist = event.pattern_match.group(2)
        song = event.pattern_match.group(3)
    track = str(artist) + " - " + str(song)
    chat = "@SpotifyMusicDownloaderBot"
    await event.edit("```Getting Your Music```")
    try:
        async with bot.conversation(chat) as conv:
            await asyncio.sleep(2)
            await event.edit("`Downloading...`")
            try:
                response = conv.wait_event(events.NewMessage(
                    incoming=True, from_users=752979930))
                msg = await bot.send_message(chat, track)
                respond = await response
                res = conv.wait_event(events.NewMessage(
                    incoming=True, from_users=752979930))
                r = await res
                """- don't spam notif -"""
                await bot.send_read_acknowledge(conv.chat_id)
            except YouBlockedUserError:
                await event.reply("`Unblock `@SpotifyMusicDownloaderBot` and retry`")
                return
            await bot.forward_messages(event.chat_id, respond.message)
        await event.client.delete_messages(
            conv.chat_id, [msg.id, r.id, respond.id]
        )
        await event.delete()
    except TimeoutError:
        return await event.edit("`Error: `@SpotifyMusicDownloaderBot` is not responding!.`")


@register(outgoing=True, pattern=r"^\.vsong(?: |$)(.*)")
async def _(event):
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    reply = await event.get_reply_message()
    if event.pattern_match.group(1):
        query = event.pattern_match.group(1)
        await event.edit("`Wait..! I am finding your videosong..`")
    elif reply:
        query = str(reply.message)
        await event.edit("`Wait..! I am finding your videosong..`")
    else:
        await event.edit("`What I am Supposed to find?`")
        return
    await getmusicvideo(query)
    l = glob.glob(("*.mp4")) + glob.glob(("*.mkv")) + glob.glob(("*.webm"))
    if l:
        await event.edit("`Yeah..! i found something..`")
    else:
        await event.edit(f"`Sorry..! i can't find anything with` **{query}**")
        return
    try:
        loa = l[0]
        metadata = extractMetadata(createParser(loa))
        duration = 0
        width = 0
        height = 0
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds
        if metadata.has("width"):
            width = metadata.get("width")
        if metadata.has("height"):
            height = metadata.get("height")
        os.system("cp *mp4 thumb.mp4")
        os.system("ffmpeg -i thumb.mp4 -vframes 1 -an -s 480x360 -ss 5 thumb.jpg")
        thumb_image = "thumb.jpg"
        c_time = time.time()
        await event.client.send_file(
            event.chat_id,
            loa,
            force_document=False,
            thumb=thumb_image,
            allow_cache=False,
            caption=query,
            supports_streaming=True,
            reply_to=reply_to_id,
            attributes=[
                DocumentAttributeVideo(
                    duration=duration,
                    w=width,
                    h=height,
                    round_message=False,
                    supports_streaming=True,
                )
            ],
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, event, c_time, "[UPLOAD]", loa)
            ),
        )
        await event.edit(f"**{query}** `Uploaded Successfully..!`")
        os.remove(thumb_image)
        os.system("rm -rf *.mkv")
        os.system("rm -rf *.mp4")
        os.system("rm -rf *.webm")
    except BaseException:
        os.remove(thumb_image)
        os.system("rm -rf *.mkv")
        os.system("rm -rf *.mp4")
        os.system("rm -rf *.webm")
        return

CMD_HELP.update({
    "getmusic":
    ".songn <Artist - Song Title>"
    "\nUsage: Download music by name (@WooMaiBot)"
    "\n\n.songf <Artist - Song Title>"
    "\nUsage: Download music by name (@SpotifyMusicDownloaderBot)"
    "\n\n.songn now"
    "\nUsage: Download current LastFM scrobble with @WooMaiBot"
    "\n\n.songf now"
    "\nUsage: Download current LastFM scrobble with @SpotifyMusicDownloaderBot"
    "\n\n.vsong <Artist - Song Title>"
    "\nUsage: Finding and uploading videoclip.\n"

})
