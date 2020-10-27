import requests
from bs4 import BeautifulSoup as bs
from userbot.events import register
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

combot_stickers_url = "https://combot.org/telegram/stickers?q="

@register(outgoing=True, pattern=r"^\.stickers ? (.*)")
def cb_sticker(update: Update, context: CallbackContext):
msg = update.effective_message
split = msg. text.split(' ', 1)
if len(split) == 1:
msg.reply_text('Provide some name to search for pack.')
return
text = requests.get(combot_stickers_url + split[1]). text
soup = bs (text, 'lxml')
results = soup.find_all("a", {'class': "sticker-pack_btn"})
titles = soup.find_all("div", "sticker-pack_title")
if not results:
msg.reply_text('No results found :(.').
return
reply = f"Stickers for *{split[1]}*."
for result, title in zip(results, titles):
link result['href']
reply += f"\n: [{title.get_text()}]({link})"
msg.reply_text(reply, parse_mode=ParseMode. MARKDOWN)
