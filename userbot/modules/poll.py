import random

from userbot import bot
from userbot.events import register

@register(pattern="^.poll(?: |$)(.*)", outgoing=True)
async def create_poll(event):
    """" Create poll """
    options = ["Yes, Sure 😎", "No interest 🙄", "What..? 😳😳🤔🤔"]
    anonymous = True
    if replied:
        query = "Do you agree with that replied Suggestion..?"
        event_id = replied.message_id
        await bot.send_poll(
            chat_id=event.chat.id,
            question=query,
            options=options,
            is_anonymous=anonymous,
            reply_to_message_id=reply_to_id)
    else:
        query = "Do you agree with that Suggestion..?"
        await bot.send_poll(
            chat_id=event.chat.id,
            question=query,
            options=options,
            is_anonymous=anonymous)
    await event.delete()
