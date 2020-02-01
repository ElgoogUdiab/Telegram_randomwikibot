from telegram.ext import Updater
import json
from telegram.ext import CommandHandler
import logging
import requests
import wikipediaapi

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_LANG = 'en'

try:
    with open("token") as f:
        token = f.readline().strip()
except:
    print("No token! Create file named \"token\" under the same directory with main.py!")
    exit(1)
try:
    with open("language.json") as f:
        language = json.load(f)
except:
    language={}

updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

url = "https://{lang}.wikipedia.org/wiki/Special:Random"

def update_language(chat_id, lang):
    global language
    language.update({str(chat_id): lang})
    with open("language.json", "w") as f:
        json.dump(language, f)

def start(update, context):
    # context.bot.send_message(chat_id=update.effective_chat.id, text=str(update.effective_chat.id))
    update_language({str(update.effective_chat.id), DEFAULT_LANG})

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def set_language(update, context):
    try:
        lang = context.args[0]
    except:
        lang = language[str(update.effective_chat.id)]
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'The current language is {lang}\nTo set language, use /language <language_abbr>')
        return
    try:
        requests.get(f"https://{lang}.wikipedia.org")
    except requests.exceptions.ConnectionError:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Language seems not exists')
        return
    update_language(update.effective_chat.id, lang)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Language saved: {lang}')

language_handler = CommandHandler('language', set_language, pass_args=True)
dispatcher.add_handler(language_handler)

def get_random_page(update, context):
    try:
        lang = language[str(update.effective_chat.id)]
    except:
        lang = DEFAULT_LANG
    r=requests.get(url.format(lang=lang))
    context.bot.send_message(chat_id=update.effective_chat.id, text=r.url)
    
get_random_page_handler = CommandHandler('random', get_random_page)
dispatcher.add_handler(get_random_page_handler)

def get_wiki_page(update, context):
    try:
        lang = language[str(update.effective_chat.id)]
    except:
        lang = DEFAULT_LANG
    if len(context.args) < 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Usage: /wiki <name>\n Remember to pre-check the language option.')
        return
    keyword = " ".join(context.args)
    wiki = wikipediaapi.Wikipedia(lang)
    page = wiki.page(keyword)
    if page.exists():
        context.bot.send_message(chat_id=update.effective_chat.id, text=page.fullurl)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="The page seems missing.")
get_wiki_handler = CommandHandler('wiki', get_wiki_page, pass_args=True)
dispatcher.add_handler(get_wiki_handler)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
dispatcher.add_error_handler(error)

updater.start_polling()
