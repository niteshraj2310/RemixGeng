import importlib.util, time, re, bs4, asyncio, requests, json, datetime, time, os
from telethon import events
from PIL import Image, ImageColor
from userbot import bot
from userbot.events import register
from telethon.errors import rpcbaseerrors

@register(pattern="^.poll(?: |$)(.*)", outgoing=True)
async def _(event):
    reply_message = await event.get_reply_message()
    if reply_message.media is None:
        await event.edit("Please reply to a media_type == @gPoll to view the questions and answers")
    elif reply_message.media.poll is None:
        await event.edit("Please reply to a media_type == @gPoll to view the questions and answers")
    else:
        media = reply_message.media
        poll = media.poll
        closed_status = poll.closed
        answers = poll.answers
        question = poll.question
        edit_caption = """Poll is Closed: {}
Question: {}
Answers: \n""".format(closed_status, question)
        if closed_status:
            results = media.results
            i = 0
            for result in results.results:
                edit_caption += "{}> {}    {}\n".format(result.option, answers[i].text, result.voters)
                i += 1
            edit_caption += "Total Voters: {}".format(results.total_voters)
        else:
            for answer in answers:
                edit_caption += "{}> {}\n".format(answer.option, answer.text)
        await event.edit(edit_caption)

@register(pattern="^.sd(?: |$)(.*)", outgoing=True)
async def selfdestruct(destroy):
    if not destroy.text[0].isalpha() and destroy.text[0] not in ("/", "#", "@", "!"):
        message = destroy.text
        counter = int(message[5:7])
        text = str(destroy.text[7:])
        text = (
            text
        )
        await destroy.delete()
        smsg = await destroy.client.send_message(destroy.chat_id, text)
        time.sleep(counter)
        await smsg.delete()


@register(pattern="^.selfd(?: |$)(.*)", outgoing=True)
async def selfdestruct(destroy):
    if not destroy.text[0].isalpha() and destroy.text[0] not in ("/", "#", "@", "!"):
        message = destroy.text
        counter = int(message[7:9])
        text = str(destroy.text[9:])
        text = (
            text
            + "\n\n`This message shall be self-destructed in "
            + str(counter)
            + " seconds`"
        )
        await destroy.delete()
        smsg = await destroy.client.send_message(destroy.chat_id, text)
        time.sleep(counter)
        await smsg.delete()

@register(pattern="^.giz(?: |$)(.*)", outgoing=True)
async def gizoogle(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    await event.edit("Processing...")
    if not input_str:
        return await event.edit("I can't gizoogle nothing.")
    try:
        result = text(input_str)
    except:
        result = "Failed to gizoogle the text."
    finally:
        return await event.edit(result)

def text(input_text: str) -> str:
        """Taken from https://github.com/chafla/gizoogle-py/blob/master/gizoogle.py"""
        params = {"translatetext": input_text}
        target_url = "http://www.gizoogle.net/textilizer.php"
        resp = requests.post(target_url, data=params)
        # the html returned is in poor form normally.
        soup_input = re.sub("/name=translatetext[^>]*>/", 'name="translatetext" >', resp.text)
        soup = bs4.BeautifulSoup(soup_input, "lxml")
        giz = soup.find_all(text=True)
        giz_text = giz[37].strip("\r\n")  # Hacky, but consistent.
        return giz_text


@register(pattern="^.color(?: |$)(.*)", outgoing=True)
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    message_id = event.message.id
    if event.reply_to_msg_id:
        message_id = event.reply_to_msg_id
    if input_str.startswith("#"):
        try:
            usercolor = ImageColor.getrgb(input_str)
        except Exception as e:
            await event.edit(str(e))
            return False
        else:
            im = Image.new(mode="RGB", size=(1280, 720), color=usercolor)
            im.save("remix.png", "PNG")
            input_str = input_str.replace("#", "#COLOR_")
            await bot.send_file(
                event.chat_id,
                "remix.png",
                force_document=False,
                caption=input_str,
                reply_to=message_id
            )
            os.remove("remix.png")
            await event.delete()
    else:
        await event.edit("Syntax: `.color <color_code>` example : `.color #ff0000`")

@register(pattern="^.calen(?: |$)(.*)", outgoing=True)
async def _(event):
    if event.fwd_from:
        return
    start = datetime.now()
    input_str = event.pattern_match.group(1)
    input_sgra = input_str.split("-")
    if len(input_sgra) == 3:
        yyyy = input_sgra[0]
        mm = input_sgra[1]
        dd = input_sgra[2]
        required_url = "https://calendar.kollavarsham.org/api/years/{}/months/{}/days/{}?lang={}".format(yyyy, mm, dd, "en")
        headers = {"Accept": "application/json"}
        response_content = requests.get(required_url, headers=headers).json()
        a = ""
        if "error" not in response_content:
            current_date_detail_arraays = response_content["months"][0]["days"][0]
            a = json.dumps(current_date_detail_arraays, sort_keys=True, indent=4)
        else:
            a = response_content["error"]
        await event.edit(str(a))
    else:
        await event.edit("SYNTAX: .calendar YYYY-MM-DD")
    end = datetime.now()
    ms = (end - start).seconds
