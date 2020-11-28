# Copyright (C) 2020 Adek Maulana.
# All rights reserved.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
"""
   Heroku manager for your userbot
"""
import asyncio
import codecs
import math
import os
from operator import itemgetter

import aiohttp
import heroku3
import requests

from userbot import (BOTLOG, BOTLOG_CHATID, CMD_HELP, HEROKU_API_KEY,
                     HEROKU_API_KEY_FALLBACK, HEROKU_APP_NAME, fallback,
                     heroku)
from userbot.events import register

useragent = (
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/81.0.4044.117 Mobile Safari/537.36"
)

heroku_api = "https://api.heroku.com"
if HEROKU_APP_NAME is not None and HEROKU_API_KEY is not None:
    Heroku = heroku3.from_key(HEROKU_API_KEY)
    app = Heroku.app(HEROKU_APP_NAME)
    heroku_var = app.config()
else:
    app = None
"""
   ConfigVars setting, get current var, set var or delete var...
"""


@register(outgoing=True, pattern=r"^.(get|del) var(?: |$)(\w*)")
async def variable(var):
    exe = var.pattern_match.group(1)
    if app is None:
        await var.edit("`[HEROKU]" "\nPlease setup your`  **HEROKU_APP_NAME**.")
        return False
    if exe == "get":
        await var.edit("`Getting information...`")
        variable = var.pattern_match.group(2)
        if variable != "":
            if variable in heroku_var:
                if BOTLOG:
                    await var.client.send_message(
                        BOTLOG_CHATID,
                        "#CONFIGVAR\n\n"
                        "**ConfigVar**:\n"
                        f"`{variable}` = `{heroku_var[variable]}`\n",
                    )
                    await var.edit("`Received to BOTLOG_CHATID...`")
                    return True
                await var.edit("`Please set BOTLOG to True...`")
                return False
            else:
                await var.edit("`Information don't exists...`")
                return True
        else:
            configvars = heroku_var.to_dict()
            if BOTLOG:
                msg = ""
                for item in configvars:
                    msg += f"`{item}` = `{configvars[item]}`\n"
                await var.client.send_message(
                    BOTLOG_CHATID, "#CONFIGVARS\n\n" "**ConfigVars**:\n" f"{msg}"
                )
                await var.edit("`Received to BOTLOG_CHATID...`")
                return True
            await var.edit("`Please set BOTLOG to True...`")
            return False
    elif exe == "del":
        await var.edit("`Deleting information...`")
        variable = var.pattern_match.group(2)
        if variable == "":
            await var.edit("`Specify ConfigVars you want to del...`")
            return False
        if variable in heroku_var:
            if BOTLOG:
                await var.client.send_message(
                    BOTLOG_CHATID,
                    "#DELCONFIGVAR\n\n" "**Delete ConfigVar**:\n" f"`{variable}`",
                )
            await var.edit("`Information deleted...`")
            del heroku_var[variable]
        else:
            await var.edit("`Information don't exists...`")
            return True


@register(outgoing=True, pattern=r"^.set var (\w*) ([\s\S]*)")
async def set_var(var):
    await var.edit("`Setting information...`")
    variable = var.pattern_match.group(1)
    value = var.pattern_match.group(2)
    if variable in heroku_var:
        if BOTLOG:
            await var.client.send_message(
                BOTLOG_CHATID,
                "#SETCONFIGVAR\n\n"
                "**Change ConfigVar**:\n"
                f"`{variable}` = `{value}`",
            )
        await var.edit("`Information sets...`")
    else:
        if BOTLOG:
            await var.client.send_message(
                BOTLOG_CHATID,
                "#ADDCONFIGVAR\n\n" "**Add ConfigVar**:\n" f"`{variable}` = `{value}`",
            )
        await var.edit("`Information added...`")
    heroku_var[variable] = value


"""
    Check account quota, remaining quota, used quota, used app quota
"""


@register(outgoing=True, pattern=r"^.usage(?: |$)")
async def dyno_usage(dyno):
    """
    Get your account Dyno Usage
    """
    await dyno.edit("`Getting Information...`")
    user_id = Heroku.account().id
    path = "/accounts/" + user_id + "/actions/get-quota"
    async with aiohttp.ClientSession() as session:
        useragent = (
            "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/81.0.4044.117 Mobile Safari/537.36"
        )
        headers = {
            "User-Agent": useragent,
            "Authorization": f"Bearer {HEROKU_API_KEY}",
            "Accept": "application/vnd.heroku+json; version=3.account-quotas",
        }
        async with session.get(heroku_api + path, headers=headers) as r:
            if r.status != 200:
                await dyno.client.send_message(
                    dyno.chat_id, f"`{r.reason}`", reply_to=dyno.id
                )
                await dyno.edit("`Can't get information...`")
                return False
            result = await r.json()
            quota = result["account_quota"]
            quota_used = result["quota_used"]
            """ - User Quota Limit and Used - """
            remaining_quota = quota - quota_used
            percentage = math.floor(remaining_quota / quota * 100)
            minutes_remaining = remaining_quota / 60
            hours = math.floor(minutes_remaining / 60)
            minutes = math.floor(minutes_remaining % 60)
            """ - User App Used Quota - """
            Apps = result["apps"]
            for apps in Apps:
                if apps.get("app_uuid") == app.id:
                    AppQuotaUsed = apps.get("quota_used") / 60
                    AppPercentage = math.floor(apps.get("quota_used") * 100 / quota)
                    break
            else:
                AppQuotaUsed = 0
                AppPercentage = 0

            AppHours = math.floor(AppQuotaUsed / 60)
            AppMinutes = math.floor(AppQuotaUsed % 60)

            await dyno.edit(
                "**Dyno Usage**:\n\n"
                f" -> `Dyno usage for`  **{app.name}**:\n"
                f"     •  **{AppHours} hour(s), "
                f"{AppMinutes} minute(s)  -  {AppPercentage}%**"
                "\n-------------------------------------------------------------\n"
                " -> `Dyno hours quota remaining this month`:\n"
                f"     •  **{hours} hour(s), {minutes} minute(s)  "
                f"-  {percentage}%**"
            )
            return True


@register(
    outgoing=True,
    pattern=(
        "^.dyno "
        "(on|restart|off|usage|cancel deploy|cancel build"
        "|get log)(?: (.*)|$)"
    ),
)
async def dyno_manage(dyno):
    """ - Restart/Kill dyno - """
    await dyno.edit("`Sending information...`")
    app = heroku.app(HEROKU_APP_NAME)
    exe = dyno.pattern_match.group(1)
    if exe == "on":
        try:
            Dyno = app.dynos()[0]
        except IndexError:
            app.scale_formation_process("worker", 1)
            text = f"`Starting` ⬢**{HEROKU_APP_NAME}**"
            sleep = 1
            dot = "."
            await dyno.edit(text)
            while sleep <= 24:
                await dyno.edit(text + f"`{dot}`")
                await asyncio.sleep(1)
                if len(dot) == 3:
                    dot = "."
                else:
                    dot += "."
                sleep += 1
            state = Dyno.state
            if state == "up":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `up...`")
            elif state == "crashed":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `crashed...`")
            return await dyno.delete()
        else:
            return await dyno.edit(f"⬢**{HEROKU_APP_NAME}** `already on...`")
    if exe == "restart":
        try:
            """ - Catch error if dyno not on - """
            Dyno = app.dynos()[0]
        except IndexError:
            return await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `is not on...`")
        else:
            text = f"`Restarting` ⬢**{HEROKU_APP_NAME}**"
            Dyno.restart()
            sleep = 1
            dot = "."
            await dyno.edit(text)
            while sleep <= 24:
                await dyno.edit(text + f"`{dot}`")
                await asyncio.sleep(1)
                if len(dot) == 3:
                    dot = "."
                else:
                    dot += "."
                sleep += 1
            state = Dyno.state
            if state == "up":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `restarted...`")
            elif state == "crashed":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `crashed...`")
            return await dyno.delete()
    elif exe == "off":
        """ - Complete shutdown - """
        app.scale_formation_process("worker", 0)
        text = f"`Shutdown` ⬢**{HEROKU_APP_NAME}**"
        sleep = 1
        dot = "."
        while sleep <= 3:
            await dyno.edit(text + f"`{dot}`")
            await asyncio.sleep(1)
            dot += "."
            sleep += 1
        await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `turned off...`")
        return await dyno.delete()
    elif exe == "usage":
        """ - Get your account Dyno Usage - """
        await dyno.edit("`Getting information...`")
        headers = {
            "User-Agent": useragent,
            "Accept": "application/vnd.heroku+json; version=3.account-quotas",
        }
        user_id = [heroku.account().id]
        if fallback is not None:
            user_id.append(fallback.account().id)
        msg = ""
        for aydi in user_id:
            if fallback is not None and fallback.account().id == aydi:
                headers["Authorization"] = f"Bearer {HEROKU_API_KEY_FALLBACK}"
            else:
                headers["Authorization"] = f"Bearer {HEROKU_API_KEY}"
            path = "/accounts/" + aydi + "/actions/get-quota"
            r = requests.get(heroku_api + path, headers=headers)
            if r.status_code != 200:
                await dyno.edit("`Cannot get information...`")
                continue
            result = r.json()
            quota = result["account_quota"]
            quota_used = result["quota_used"]
            """ - Used - """
            remaining_quota = quota - quota_used
            percentage = math.floor(remaining_quota / quota * 100)
            minutes_remaining = remaining_quota / 60
            hours = math.floor(minutes_remaining / 60)
            minutes = math.floor(minutes_remaining % 60)
            """ - Used per/App Usage - """
            Apps = result["apps"]
            """ - Sort from larger usage to lower usage - """
            Apps = sorted(Apps, key=itemgetter("quota_used"), reverse=True)
            if fallback is not None and fallback.account().id == aydi:
                apps = fallback.apps()
                msg += "**Dyno Usage fallback-account**:\n\n"
            else:
                apps = heroku.apps()
                msg += "**Dyno Usage main-account**:\n\n"
            try:
                Apps[0]
            except IndexError:
                """ - If all apps usage are zero - """
                for App in apps:
                    msg += (
                        f" -> `Dyno usage for`  **{App.name}**:\n"
                        f"     •  `0`**h**  `0`**m**  "
                        f"**|**  [`0`**%**]\n\n"
                    )
            for App in Apps:
                AppName = "__~~Deleted or transferred app~~__"
                ID = App.get("app_uuid")
                try:
                    AppQuota = App.get("quota_used")
                    AppQuotaUsed = AppQuota / 60
                    AppPercentage = math.floor(AppQuota * 100 / quota)
                except IndexError:
                    AppQuotaUsed = 0
                    AppPercentage = 0
                finally:
                    AppHours = math.floor(AppQuotaUsed / 60)
                    AppMinutes = math.floor(AppQuotaUsed % 60)
                    for names in apps:
                        if ID == names.id:
                            AppName = f"**{names.name}**"
                            break
                    msg += (
                        f" -> `Dyno usage for`  {AppName}:\n"
                        f"     •  `{AppHours}`**h**  `{AppMinutes}`**m**  "
                        f"**|**  [`{AppPercentage}`**%**]\n\n"
                    )
            msg = (
                f"{msg}"
                " -> `Dyno hours quota remaining this month`:\n"
                f"     •  `{hours}`**h**  `{minutes}`**m**  "
                f"**|**  [`{percentage}`**%**]\n\n"
            )
        if msg:
            return await dyno.edit(msg)
        return
    elif exe in ["cancel deploy", "cancel build"]:
        """ - Only cancel 1 recent builds from activity - """
        build_id = dyno.pattern_match.group(2)
        if build_id is None:
            build = app.builds(order_by="created_at", sort="desc")[0]
        else:
            build = app.builds().get(build_id)
            if build is None:
                return await dyno.edit(f"`There is no such build.id`:  **{build_id}**")
        if build.status != "pending":
            return await dyno.edit("`Zero active builds to cancel...`")
        headers = {
            "User-Agent": useragent,
            "Authorization": f"Bearer {HEROKU_API_KEY}",
            "Accept": "application/vnd.heroku+json; version=3.cancel-build",
        }
        path = "/apps/" + build.app.id + "/builds/" + build.id
        r = requests.delete(heroku_api + path, headers=headers)
        text = f"`Stopping build`  ⬢**{build.app.name}**"
        await dyno.edit(text)
        sleep = 1
        dot = "."
        await asyncio.sleep(2)
        while sleep <= 3:
            await dyno.edit(text + f"`{dot}`")
            await asyncio.sleep(1)
            dot += "."
            sleep += 1
        await dyno.respond("`[HEROKU]`\n" f"Build: ⬢**{build.app.name}**  `Stopped...`")
        """ - Restart main if builds cancelled - """
        try:
            app.dynos()[0].restart()
        except IndexError:
            await dyno.edit("`Your dyno main app is not on...`")
            await asyncio.sleep(2.5)
        return await dyno.delete()
    elif exe == "get log":
        await dyno.edit("`Getting information...`")
        with open("logs.txt", "w") as log:
            log.write(app.get_log())
        await dyno.client.send_file(
            dyno.chat_id,
            "logs.txt",
            reply_to=dyno.id,
            caption="`Main dyno logs...`",
        )
        await dyno.edit("`Information gets and sent back...`")
        await asyncio.sleep(5)
        await dyno.delete()
        return os.remove("logs.txt")


@register(outgoing=True, pattern=r"^\.logs")
async def _(dyno):
    try:
        Heroku = heroku3.from_key(HEROKU_API_KEY)
        app = Heroku.app(HEROKU_APP_NAME)
    except BaseException:
        return await dyno.reply(
            "`Please make sure your Heroku API Key, Your App name are configured correctly in the heroku var.`"
        )
    await dyno.edit("`Getting Logs....`")
    with open("logs.txt", "w") as log:
        log.write(app.get_log())
    fd = codecs.open("logs.txt", "r", encoding="utf-8")
    data = fd.read()
    key = (
        requests.post("https://nekobin.com/api/documents", json={"content": data})
        .json()
        .get("result")
        .get("key")
    )
    url = f"https://nekobin.com/raw/{key}"
    await dyno.edit(f"`Here the heroku logs:`\n\nPasted to: [Nekobin]({url})")
    return os.remove("logs.txt")


CMD_HELP.update(
    {
        "heroku": ">**Dyno components.**\
    \n>`.dyno usage`\
    \nUsage: Check your heroku App usage dyno quota.\
    \nIf one of your app usage is empty, it won't be write in output.\
    \n\n>`.dyno on`\
    \nUsage: Turn on your main dyno application.\
    \n\n>`.dyno restart`\
    \nUsage: Restart your dyno application.\
    \n\n>`.dyno off`\
    \nUsage: Shutdown dyno completly.\
    \n\n>`.dyno cancel deploy` or >`.dyno cancel build`\
    \nUsage: Cancel deploy from main app.\
    \nGive build.id to specify build to cancel.\
    \n\n>`.dyno get log`\
    \nUsage: Get your main dyno recent logs."
    }
)
