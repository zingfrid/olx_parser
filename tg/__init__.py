import time
from typing import List

from telegram import Bot

from config import logger
from config import settings
from utils.models import NewAdModel


def send_message_into_telegram(bot: Bot, new_ads: List[NewAdModel]) -> None:
    bot = Bot(token=settings.TELEGRAM_BOT_KEY)
    for chat in settings.TELEGRAM_CHAT_IDS:
        print (chat)
        for item in reversed(new_ads):
            text = f'''\n{item.phones} == {item.price}\n{item.url}'''
            try:
                bot.send_message(chat_id=chat, text=text)
                time.sleep(0.250)
            except Exception:  # pylint: disable=broad-except
                logger.exception('=== Error during sending message via Telegram ===')
