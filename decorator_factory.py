from telegram.bot import Bot
from telegram.ext import Updater
from telegram import ChatAction


def decorate(action_type=ChatAction.TYPING):
    def decorater(func):
        def apply_decorater(*args, **kwargs):
            if not isinstance(args[0], Bot) and not isinstance(args[1], Updater):
                raise Exception(f"Bot|Updater instance not received when calling {func}")
            chat_id = args[1].effective_message.chat_id
            args[0].send_chat_action(chat_id=chat_id, action=action_type)
            func(*args, **kwargs)

        return apply_decorater

    return decorater
