"""ported from Catuserbot module modified by  @mrconfused""""

import json
import logging
import os
import random
import textwrap
import urllib

import emoji
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont, ImageOps
from telethon.tl import functions, types
from userbot.events import register
from userbot.utils import runcmd

COLORS = [
    "#F07975",
    "#F49F69",
    "#F9C84A",
    "#8CC56E",
    "#6CC7DC",
    "#80C1FA",
    "#BCB3F9",
    "#E181AC",
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def process(msg, user, client, reply, replied=None):
    if not os.path.isdir("./temp/"):
        os.mkdir("./temp/", 0o755)
    urllib.request.urlretrieve(
        "https://github.com/erenmetesar/modules-repo/raw/master/Roboto-Regular.ttf",
        "./temp/Roboto-Regular.ttf",
    )
    urllib.request.urlretrieve(
        "https://github.com/erenmetesar/modules-repo/raw/master/Quivira.otf",
        "./temp/Quivira.otf",
    )
    urllib.request.urlretrieve(
        "https://github.com/erenmetesar/modules-repo/raw/master/Roboto-Medium.ttf",
        "./temp/Roboto-Medium.ttf",
    )
    urllib.request.urlretrieve(
        "https://github.com/erenmetesar/modules-repo/raw/master/DroidSansMono.ttf",
        "./temp/DroidSansMono.ttf",
    )
    urllib.request.urlretrieve(
        "https://github.com/erenmetesar/modules-repo/raw/master/Roboto-Italic.ttf",
        "./temp/Roboto-Italic.ttf",
    )

    # Importıng fonts and gettings the size of text
    font = ImageFont.truetype(
        "./temp/Roboto-Medium.ttf",
        43,
        encoding="utf-16")
    font2 = ImageFont.truetype(
        "./temp/Roboto-Regular.ttf",
        33,
        encoding="utf-16")
    mono = ImageFont.truetype(
        "./temp/DroidSansMono.ttf",
        30,
        encoding="utf-16")
    italic = ImageFont.truetype(
        "./temp/Roboto-Italic.ttf", 33, encoding="utf-16")
    fallback = ImageFont.truetype("./temp/Quivira.otf", 43, encoding="utf-16")

    # Splitting text
    maxlength = 0
    width = 0
    text = []
    for line in msg.split("\n"):
        length = len(line)
        if length > 43:
            text += textwrap.wrap(line, 43)
            maxlength = 43
            if width < fallback.getsize(line[:43])[0]:
                if "MessageEntityCode" in str(reply.entities):
                    width = mono.getsize(line[:43])[0] + 30
                else:
                    width = fallback.getsize(line[:43])[0]
        else:
            text.append(line + "\n")
            if width < fallback.getsize(line)[0]:
                if "MessageEntityCode" in str(reply.entities):
                    width = mono.getsize(line)[0] + 30
                else:
                    width = fallback.getsize(line)[0]
            if maxlength < length:
                maxlength = length

    title = ""
    try:
        details = await client(
            functions.channels.GetParticipantRequest(reply.chat_id, user.id)
        )
        if isinstance(details.participant, types.ChannelParticipantCreator):
            title = details.participant.rank if details.participant.rank else "Creator"
        elif isinstance(details.participant, types.ChannelParticipantAdmin):
            title = details.participant.rank if details.participant.rank else "Admin"
    except TypeError:
        pass
    titlewidth = font2.getsize(title)[0]

    # Get user name
    lname = "" if not user.last_name else user.last_name
    tot = user.first_name + " " + lname

    namewidth = fallback.getsize(tot)[0] + 10

    if namewidth > width:
        width = namewidth
    width += titlewidth + 30 if titlewidth > width - \
        namewidth else -(titlewidth - 30)
    height = len(text) * 40

    # Profile Photo BG
    pfpbg = Image.new("RGBA", (125, 600), (0, 0, 0, 0))

    # Draw Template
    top, middle, bottom = await drawer(width, height)
    # Profile Photo Check and Fetch
    yes = False
    color = random.choice(COLORS)
    async for photo in client.iter_profile_photos(user, limit=1):
        yes = True
    if yes:
        pfp = await client.download_profile_photo(user)
        paste = Image.open(pfp)
        os.remove(pfp)
        paste.thumbnail((105, 105))

        # Mask
        mask_im = Image.new("L", paste.size, 0)
        draw = ImageDraw.Draw(mask_im)
        draw.ellipse((0, 0, 105, 105), fill=255)

        # Apply Mask
        pfpbg.paste(paste, (0, 0), mask_im)
    else:
        paste, color = await no_photo(user, tot)
        pfpbg.paste(paste, (0, 0))

    # Creating a big canvas to gather all the elements
    canvassize = (
        middle.width + pfpbg.width,
        top.height + middle.height + bottom.height,
    )
    canvas = Image.new("RGBA", canvassize)
    draw = ImageDraw.Draw(canvas)

    y = 80
    if replied:
        # Creating a big canvas to gather all the elements
        replname = "" if not replied.sender.last_name else replied.sender.last_name
        reptot = replied.sender.first_name + " " + replname
        font2.getsize(reptot)[0]
        if reply.sticker:
            sticker = await reply.download_media()
            file_1 = os.path.join("./temp/", "q.png")
            if sticker.endswith(("tgs")):
                cmd = (
                    f"lottie_convert.py --frame 0 -if lottie -of png {sticker} {file_1}"
                )
                stdout, stderr = (await runcmd(cmd))[:2]
                stimg = Image.open("./temp/q.png")
            else:
                stimg = Image.open(sticker)
            canvas = canvas.resize(
                (stimg.width + pfpbg.width + 30, stimg.height + 10))
            canvas.paste(pfpbg, (0, 0))
            canvas.paste(stimg, (pfpbg.width + 10, 10))
            os.remove(sticker)
            if os.path.lexists(file_1):
                os.remove(file_1)
            return True, canvas
        canvas = canvas.resize((canvas.width + 60, canvas.height + 120))
        top, middle, bottom = await drawer(middle.width + 60, height + 105)
        canvas.paste(pfpbg, (0, 0))
        canvas.paste(top, (pfpbg.width, 0))
        canvas.paste(middle, (pfpbg.width, top.height))
        canvas.paste(bottom, (pfpbg.width, top.height + middle.height))
        draw = ImageDraw.Draw(canvas)
        if replied.sticker:
            replied.text = "Sticker"
        elif replied.photo:
            replied.text = "Photo"
        elif replied.audio:
            replied.text = "Audio"
        elif replied.voice:
            replied.text = "Voice Message"
        elif replied.document:
            replied.text = "Document"
        await replied_user(
            draw,
            reptot,
            replied.message.replace("\n", " "),
            maxlength + len(title),
            len(title),
        )
        y = 200
    elif reply.sticker:
        sticker = await reply.download_media()
        file_1 = os.path.join("./temp/", "q.png")
        if sticker.endswith(("tgs")):
            cmd = f"lottie_convert.py --frame 0 -if lottie -of png {sticker} {file_1}"
            stdout, stderr = (await runcmd(cmd))[:2]
            stimg = Image.open("./temp/q.png")
        else:
            stimg = Image.open(sticker)
        canvas = canvas.resize(
            (stimg.width + pfpbg.width + 30, stimg.height + 10))
        canvas.paste(pfpbg, (0, 0))
        canvas.paste(stimg, (pfpbg.width + 10, 10))
        os.remove(sticker)
        if os.path.lexists(file_1):
            os.remove(file_1)
        return True, canvas
    elif reply.document and not reply.audio:
        docname = ".".join(
            reply.document.attributes[-1].file_name.split(".")[:-1])
        doctype = reply.document.attributes[-1].file_name.split(
            ".")[-1].upper()
        if reply.document.size < 1024:
            docsize = str(reply.document.size) + " Bytes"
        elif reply.document.size < 1048576:
            docsize = str(round(reply.document.size / 1024, 2)) + " KB "
        elif reply.document.size < 1073741824:
            docsize = str(round(reply.document.size / 1024 ** 2, 2)) + " MB "
        else:
            docsize = str(round(reply.document.size / 1024 ** 3, 2)) + " GB "
        docbglen = (
            font.getsize(docsize)[0]
            if font.getsize(docsize)[0] > font.getsize(docname)[0]
            else font.getsize(docname)[0]
        )
        canvas = canvas.resize((pfpbg.width + width + docbglen, 160 + height))
        top, middle, bottom = await drawer(width + docbglen, height + 30)
        canvas.paste(pfpbg, (0, 0))
        canvas.paste(top, (pfpbg.width, 0))
        canvas.paste(middle, (pfpbg.width, top.height))
        canvas.paste(bottom, (pfpbg.width, top.height + middle.height))
        canvas = await catdoctype(docname, docsize, doctype, canvas)
        y = 80 if text else 0
    else:
        canvas.paste(pfpbg, (0, 0))
        canvas.paste(top, (pfpbg.width, 0))
        canvas.paste(middle, (pfpbg.width, top.height))
        canvas.paste(bottom, (pfpbg.width, top.height + middle.height))
        y = 85

    # Writing User's Name
    space = pfpbg.width + 30
    namefallback = ImageFont.truetype(
        "./temp/Quivira.otf", 43, encoding="utf-16")
    for letter in tot:
        if letter in emoji.UNICODE_EMOJI:
            newemoji, mask = await emoji_fetch(letter)
            canvas.paste(newemoji, (space, 24), mask)
            space += 40
        else:
            if not await fontTest(letter):
                draw.text((space, 20), letter, font=namefallback, fill=color)
                space += namefallback.getsize(letter)[0]
            else:
                draw.text((space, 20), letter, font=font, fill=color)
                space += font.getsize(letter)[0]

    if title:
        draw.text((canvas.width - titlewidth - 20, 25),
                  title, font=font2, fill="#898989")

    # Writing all separating emojis and regular texts
    x = pfpbg.width + 30
    bold, mono, italic, link = await get_entity(reply)
    index = 0
    emojicount = 0
    textfallback = ImageFont.truetype(
        "./temp/Quivira.otf", 33, encoding="utf-16")
    textcolor = "white"
    for line in text:
        for letter in line:
            index = (msg.find(letter) if emojicount ==
                     0 else msg.find(letter) + emojicount)
            for offset, length in bold.items():
                if index in range(offset, length):
                    font2 = ImageFont.truetype(
                        "./temp/Roboto-Medium.ttf", 33, encoding="utf-16"
                    )
                    textcolor = "white"
            for offset, length in italic.items():
                if index in range(offset, length):
                    font2 = ImageFont.truetype(
                        "./temp/Roboto-Italic.ttf", 33, encoding="utf-16"
                    )
                    textcolor = "white"
            for offset, length in mono.items():
                if index in range(offset, length):
                    font2 = ImageFont.truetype(
                        "./temp/DroidSansMono.ttf", 30, encoding="utf-16"
                    )
                    textcolor = "white"
            for offset, length in link.items():
                if index in range(offset, length):
                    font2 = ImageFont.truetype(
                        "./temp/Roboto-Regular.ttf", 30, encoding="utf-16"
                    )
                    textcolor = "#898989"
            if letter in emoji.UNICODE_EMOJI:
                newemoji, mask = await emoji_fetch(letter)
                canvas.paste(newemoji, (x, y - 2), mask)
                x += 45
                emojicount += 1
            else:
                if not await fontTest(letter):
                    draw.text(
                        (x, y), letter, font=textfallback, fill=textcolor)
                    x += textfallback.getsize(letter)[0]
                else:
                    draw.text((x, y), letter, font=font2, fill=textcolor)
                    x += font2.getsize(letter)[0]
            msg = msg.replace(letter, "¶", 1)
        y += 40
        x = pfpbg.width + 30
    return True, canvas


@register(outgoing=True, pattern="^.pch(?: |$)(.*)", disable_errors=True)
async def stickerchat(event):
    if event.fwd_from:
        return
    await event.edit("```Sir wait plox else gey...```")
    await event.delete()
    reply = await event.get_reply_message()
    if not reply:
        await event.edit("I cant quote the message . reply to a message")
        return
    fetchmsg = reply.message
    repliedreply = await reply.get_reply_message()
    if reply.media:
        if reply.media.document.mime_type in ("mp4"):
            await event.edit("animated stickers and mp4 formats are not supported")
            return
    await event.delete()
    user = (
        await bot.get_entity(reply.forward.sender) if reply.fwd_from else reply.sender
    )
    res, qmsg = await process(fetchmsg, user, borg, reply, repliedreply)
    if not res:
        return
    qmsg.save("./temp/sticker.webp")
    await bot.send_file(event.chat_id, "./temp/sticker.webp", reply_to=reply)
    os.remove("./temp/sticker.webp")
