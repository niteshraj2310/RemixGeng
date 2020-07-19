"""Globally Ban users from all the
Group Administrations bots where you are SUDO
Available Commands:
.gban REASON
.ungban REASON"""
import asyncio
from userbot.events import register 
from userbot import  CMD_HELP, bot, G_BAN_LOGGER_GROUP, ALIVE_NAME
#imported from uniborg by @heyworld

# ================= CONSTANT =================
DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else uname().node
# ============================================

@register(outgoing=True, pattern="^.gban(?: |$)(.*)")
async def _(event):
    if G_BAN_LOGGER_GROUP is None:
        await event.edit("Set G_BAN_LOGGER_GROUP in vars otherwise module won't work.")
        return
    if event.fwd_from:
        return
    reason = event.pattern_match.group(1)
    if event.reply_to_msg_id:
        r = await event.get_reply_message()
        if r.forward:
            r_from_id = r.forward.from_id or r.from_id
        else:
            r_from_id = r.from_id
        await bot.send_message(
            G_BAN_LOGGER_GROUP,
            "/gban [user](tg://user?id={}) {}".format(r_from_id, reason)
        )
    await event.delete()
    await event.reply("**gbanning...**")
    asyncio.sleep(3.5)
    await event.reply(f"**User gbanned by {DEFAULTUSER}**")


@register(outgoing=True, pattern="^.ungban(?: |$)(.*)")
async def _(event):
    if G_BAN_LOGGER_GROUP is None:
        await event.edit("Set G_BAN_LOGGER_GROUP in vars otherwise module won't work.")
        return
    if event.fwd_from:
        return
    reason = event.pattern_match.group(1)
    if event.reply_to_msg_id:
        r = await event.get_reply_message()
        r_from_id = r.from_id
        await bot.send_message(
            G_BAN_LOGGER_GROUP,
            "/ungban [user](tg://user?id={}) {}".format(r_from_id, reason)
        )
    await event.delete()
    await event.reply("**ungbanning...**")
    asyncio.sleep(3.5)
    await event.reply(f"**User ungbanned by {DEFAULTUSER}**")
    
CMD_HELP.update({
    "gban": "\
`.gban reason`\
\nUsage: Globally Ban users from all the Group Administrations bots where you are SUDO.\
\n\n`.ungban reason`\
\nUsage: Globally unBan users from all the Group Administrations bots where you are SUDO"
})
