from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from telegram import ChatAction

import requests
import cricket_api_parser
from bot_logger import create_logger
import config

from decorator_factory import decorate

logger = create_logger(__name__)


def error_cb(bot, update, error):
    logger.error(f"Error occured => {error}")

    try:
        raise error
    except Exception as ex:
        logger.error(f"Exception caught => {ex}")


def get_url():
    content = requests.get('https://random.dog/woof.json').json()
    return content['url']


def cric_api_operations(ops="search", *args):
    data = cricket_api_parser.fetch(ops, " ".join(args[0]))
    return data


@decorate(action_type=ChatAction.UPLOAD_PHOTO)
def img_handler(bot, update):
    url = get_url()
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=url)


def joke_handler(bot, update):
    try:
        logger.info("Here in joke_handler")
        chat_id = update.message.chat_id

        content = requests.get("http://api.icndb.com/jokes/random").json()

        if content is None:

            bot.send_message(chat_id, "Sorry, Our services are currently down")
        else:

            joke = str(content['value']['id']) + "=> " + content['value']['joke']

            bot.send_message(chat_id, joke)
    except Exception as ex:
        logger.error(msg=f"Exception  occured is => {ex}")


def cricket_player_search_handler(bot, update, args):
    chat_id = update.message.chat_id

    di = cric_api_operations("search", args)
    di['chat_id'] = chat_id

    bot.send_message(**di)
    return


@decorate(action_type=ChatAction.TYPING)
def cricket_new_match_handler(bot, update):
    data = cricket_api_parser.fetch('newmatch')
    if data and type(data) == list:
        for item in data:
            item['chat_id'] = update.message.chat_id
            bot.send_message(**item)
        return

    bot.send_message(text="Sorry! We cannot find any matches.", chat_id=update.message.chat_id)
    return


def records_handler(bot, update, args):
    bot.send_message(text="Thank-you for the request. We are working on it", chat_id=update.message.chat_id)
    return


def callback_handler(bot, update):
    data = update.callback_query.data
    args = data.split(" ")
    chat_id = update.effective_message.chat_id
    reply = "We recieved your message."

    if data.startswith("record"):
        reply = cricket_api_parser.callback_handler_records(args[1])
    elif data.startswith("match"):
        reply = cricket_api_parser.callback_handler_match(args[1])

    reply['chat_id'] = chat_id

    bot.send_message(**reply)
    return


def main():
    updater = Updater(config.telegram_key)

    dp = updater.dispatcher
    dp.add_error_handler(error_cb)
    dp.add_handler(CommandHandler('img', img_handler))
    dp.add_handler(CommandHandler('joke', joke_handler))
    dp.add_handler(CommandHandler('player', cricket_player_search_handler, pass_args=True))
    dp.add_handler(CommandHandler('records', records_handler, pass_args=True))
    dp.add_handler(CommandHandler('newmatch', cricket_new_match_handler))
    dp.add_handler(CallbackQueryHandler(callback_handler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
