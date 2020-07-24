# The function convert an image to ascii art
# f: Input filename
# SC: the horizontal pixel sampling rate. It should be between 0(exclusive) and 1(inclusive). The larger the number, the more details in the output. 
#   If you want the ascii art output be the same size as input, use ~ 1/ font size width. 
# GCF: >0. It's an image tuning factor. If GCF>1, the image will look brighter; if 0<GCF<1, the image will look darker.
# out_f: output filename
# color1, color2, bgcolor: follow W3C color naming https://www.w3.org/TR/css3-color/#svg-color
#
# Copyright 2017, Shanshan Wang, MIT license
# Based on https://gist.github.com/wshanshan/c825efca4501a491447056849dd207d6
# Module by @deleteduser420

import os
import time
from PIL import Image, ImageFont, ImageDraw
from userge import userge, Message, Config
from userge.utils import progress, take_screen_shot, runcmd
import numpy as np
from colour import Color
import random
from random import randrange
'''Reply to an Media and see the Magic'''
@userge.on_cmd("ascii$", about={
    'header': "Ascii Sticker",
    'description': "transform on any gif/sticker/image to an Ascii Sticker. ",
    'usage': " {tr}ascii",
    'examples': "{tr}ascii as a reply."})
async def transform(message: Message):
    replied = message.reply_to_message
    if not replied:
        await message.err("<code>Give Me Something (¬_¬)</code>")
        await message.client.send_sticker(
            sticker="CAADAQADhgADwKwII4f61VT65CNGFgQ", chat_id=message.chat.id)
        return 
    if not (replied.photo or replied.sticker or replied.animation):
        await message.err("<code>Bruh You need help! I mean read HELP!</code>")
        return
    if not os.path.isdir(Config.DOWN_PATH):
        os.makedirs(Config.DOWN_PATH)
    await message.edit(f"<code>Converting Media!...</code>")
    c_time = time.time()

    dls = await message.client.download_media(
        message=message.reply_to_message,
        file_name=Config.DOWN_PATH,
        progress=progress,
        progress_args=(
            "Trying to Posses given content", userge, message, c_time
        )
    )
    dls_loc = os.path.join(Config.DOWN_PATH, os.path.basename(dls))
    
   
    if replied.sticker and replied.sticker.file_name.endswith(".tgs"):
        await message.edit("<code>OMG, an Animated sticker ⊙_⊙, lemme do my megik...</code>")
        png_file = os.path.join(Config.DOWN_PATH, "picture.png")
        cmd = f"lottie_convert.py --frame 0 -if lottie -of png {dls_loc} {png_file}"
        stdout, stderr = (await runcmd(cmd))[:2]
        os.remove(dls_loc)
        if not os.path.lexists(png_file):
            await message.err("<code>This sticker is BAKA, i won't ASCII it? ≧ω≦</code>")
            raise Exception(stdout + stderr)
        dls_loc = png_file

    elif replied.animation:
        await message.edit("<code>Look it's GF. Oh, no it's just a Gif</code>")
        jpg_file = os.path.join(Config.DOWN_PATH, "picture.jpg")
        await take_screen_shot(dls_loc, 0, jpg_file)
        os.remove(dls_loc)
        if not os.path.lexists(jpg_file):
            await message.err("<code>This Gif is  (｡ì _ í｡), won't ascii it.</code>")
            return
        dls_loc = jpg_file
    c_list = random_color()
    color1 = c_list[0]
    color2 = c_list[1]
    bgcolor = "#080808" 
    webp_file = asciiart(dls_loc, 0.2, 1.9, color1, color2, bgcolor)
    await message.client.send_sticker(chat_id=message.chat.id,
                                    sticker=webp_file,
                                    reply_to_message_id=replied.message_id)
    await message.delete()
    os.remove(webp_file)


def asciiart(in_f, SC, GCF, color1, color2, bgcolor):
    chars = np.asarray(list(' .,:irs?@9B&#'))
    font = ImageFont.load_default()
    letter_width = font.getsize("x")[0]
    letter_height = font.getsize("x")[1]
    WCF = letter_height/letter_width
    #open the input file
    img = Image.open(in_f)
    widthByLetter=round(img.size[0]*SC*WCF)
    heightByLetter = round(img.size[1]*SC)
    S = (widthByLetter, heightByLetter)
    img = img.resize(S)
    img = np.sum(np.asarray(img), axis=2)
    img -= img.min()
    img = (1.0 - img/img.max())**GCF*(chars.size-1)
    # Generate the ascii art symbols 
    lines = ("\n".join( ("".join(r) for r in chars[img.astype(int)]) )).split("\n")
    # Create gradient color bins
    nbins = len(lines)
    colorRange =list(Color(color1).range_to(Color(color2), nbins))
    #Create an image object, set its width and height
    newImg_width= letter_width *widthByLetter
    newImg_height = letter_height * heightByLetter
    newImg = Image.new("RGBA", (newImg_width, newImg_height), bgcolor)
    draw = ImageDraw.Draw(newImg)
    # Print symbols to image
    leftpadding=0
    y = 0
    lineIdx=0
    for line in lines:
        color = colorRange[lineIdx]
        lineIdx +=1
        draw.text((leftpadding, y), line, color.hex, font=font)
        y += letter_height
    # Save the image file
    image_name = "ascii.webp"
    webp_file = os.path.join(Config.DOWN_PATH, image_name)
    newImg.save(webp_file, "WebP")
    return webp_file

def random_color():
    number_of_colors = 2

    color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                for i in range(number_of_colors)]
    return color
