import calendar  # pylint: disable=W0406

from userbot.events import register

@register(pattern="^.(cal)(?: |$)(.*)", outgoing=True)
async def cal_(event ):

    if not event.input_str:
        await event.err(
            "I don't found any input text"
            "For more help do .help .cal")
        return
    if '|' not in event.input_str:
        await event.err("both year and month required!")
        return
    await event.edit("`Searching...`")
    year, month = message.input_str.split('|', maxsplit=1)
    try:
        input_ = calendar.month(int(year.strip()), int(month.strip()))
        await event.edit(f"```{input_}```")
    except Exception as e:
        await event.err(e)
