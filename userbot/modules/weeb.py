import jikanpy
import nekos
import os
import json
import aiohttp
import asyncio
import random
from jikanpy import Jikan
from jikanpy.exceptions import APIException
from urllib.parse import quote as urlencode
from telethon import events
from userbot.events import register
from userbot import CMD_HELP, bot
from asyncio import sleep


_pats = []
jikan = Jikan()


@register(outgoing=True, pattern=r"^.pat(?: |$)")
async def pat(e):
    global _pats


    url = 'https://headp.at/js/pats.json'
    if not _pats:
        async with aiohttp.ClientSession() as session:
            async with session.post(url) as raw_resp:
                resp = await raw_resp.text()
        _pats = json.loads(resp)
    pats = _pats

    pats = [i for i in pats if os.path.splitext(i)[1] == '.gif']

    pat = random.choice(pats)
    link = f'https://headp.at/pats/{urlencode(pat)}'

    await asyncio.wait([
        e.respond(file=link, reply_to=e.reply_to_msg_id),
        e.delete()
    ])


@register(outgoing=True, pattern="^\.pgif(?: |$)(.*)")
async def pussyg(e):
    await e.edit("`Finding some pussy gifs...`")
    await sleep(2)
    target = 'pussy'
    await bot.send_file(e.chat_id, nekos.img(target), reply_to=e.reply_to_msg_id)
    await e.delete()


@register(outgoing=True, pattern="^\.pjpg(?: |$)(.*)")
async def pussyp(e):
    await e.edit("`Finding some pussy pics...`")
    await sleep(2)
    target = 'pussy_jpg'
    await bot.send_file(e.chat_id, nekos.img(target), reply_to=e.reply_to_msg_id)
    await e.delete()


@register(outgoing=True, pattern="^\.cum(?: |$)(.*)")
async def cum(e):
    await e.edit("`Finding some cum gifs...`")
    await sleep(2)
    target = 'cum'
    await bot.send_file(e.chat_id, nekos.img(target), reply_to=e.reply_to_msg_id)
    await e.delete()


CMD_HELP.update({
    'weeb':
    "`.pgif`"
    "\nUsage: Get pussy gif.\n"
    "`.pjpg`"
    "\nUsage: Get pussy image.\n"
    "`.pat`"
    "\nUsage: Get random pat gif.\n"
    "`.cum`"
    "\nUsage: Get random cum gif."
})
