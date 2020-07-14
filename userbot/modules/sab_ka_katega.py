#"""Fun pligon...for HardcoreUserbot
#\nCode by @Hack12R
#type `.degi` and `.nehi` to see the fun.
#"""
import random, re
#from uniborg.util import admin_cmd
import asyncio
from telethon import events
from userbot.events import register
from asyncio import sleep
import time
from userbot import CMD_HELP

@register(outgoing=True, pattern="^.degi$")
async def _(event):
     if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        await event.edit("Wo")
        await asyncio.sleep(0.7)
        await event.edit("Degi")
        await asyncio.sleep(1)
        await event.edit("Tum")
        await asyncio.sleep(0.8)
        await event.edit("Ekbar")
        await asyncio.sleep(0.9)
        await event.edit("Mang")
        await asyncio.sleep(1)
        await event.edit("Kar")
        await asyncio.sleep(0.8)
        await event.edit("Toh")
        await asyncio.sleep(0.7)
        await event.edit("Dekho")
        await asyncio.sleep(1)
        await event.edit("`Wo Degi Tum Ekbar Mang Kar toh Dekho`")

@register(outgoing=True, pattern="^.nehi$")
async def _(event):
    if event.fwd_from:
        return
    await event.edit("`Wo PaKkA DeGi Tu ManG KaR ToH DekH`")
    await asyncio.sleep(999)



CMD_HELP.update({
    "degi":
    ".degi or .nehi\
\nUsage: Sabka Katega."
})    
