"""MEDIA INFO"""
# Suggested by - @d0n0t (https://github.com/code-rgb/USERGE-X/issues/9)
# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.

import os
from userbot import TEMP_DOWNLOAD_DIRECTORY
from userbot.utils import runcmd
from userbot.events import register
from html_telegraph_poster import TelegraphPoster

def post_to_telegraph(anime_title, html_format_content):
    post_client = TelegraphPoster(use_api=True)
    auth_name = "@Cheems_69"
    bish = "https://t.me/Cheems_69"
    post_client.create_api_token(auth_name)
    post_page = post_client.post(
        title=anime_title,
        author=auth_name,
        author_url=bish,
        text=html_format_content)
    return post_page["url"]


@register(outgoing=True, pattern=r"^\.media ?(.*)")
async def mediainfo(event):
    X_MEDIA = None
    reply = await event.get_reply_message()
    if not reply:
        await event.edit("reply to media first")
        return
    await event.edit("`Processing...`")
    try:
        if reply.media and reply.media.document:
            X_MEDIA = reply.media.document.mime_type
            hmm = reply.media.document.stringify()
    except BaseException:
        if reply.media and reply.media.photo:
            X_MEDIA = "photo"
            hmm = reply.media.photo.stringify()
    if not X_MEDIA:
        return await event.edit("`Reply To a Vaild Media Format`")
    if X_MEDIA.startswith(("text")):
        return await event.edit("`Reply To a Vaild Media Format`")
    file_path = await reply.download_media(TEMP_DOWNLOAD_DIRECTORY)
    out, err, ret, pid = await runcmd(f"mediainfo {file_path}")
    if not out:
        out = "Not Supported"
    body_text = f"""<br>
    <h2>JSON</h2>
    <code>{hmm}</code>
    <br>
    <br>
    <h2>DETAILS</h2>
    <code>{out}</code>
    """
    link = post_to_telegraph(f"{X_MEDIA}", body_text)

    await event.edit(
        f"ℹ️  <b>MEDIA INFO:  <a href ='{link}' > {X_MEDIA}</a></b>",
        parse_mode="HTML",
        link_preview=True,
    )

    os.remove(file_path)
