import time

from requests import session as RequestsSession
from telegram import Bot

from config import logger
from config import settings
from olx import fetch_ads
from olx import filter_new_ads
from tg import send_message_into_telegram
from ad.adapters import provider as Prov

def main():
    new_ads = []
    bot = Bot(token=settings.TELEGRAM_BOT_KEY)

#    prov = Prov.CreateProviderOlx()

#    items = []
#    for ad in Impl.get_base_ads:
#       item = Item(
#              title=ad.title,
#              link=ad.url,
#              description=_get_detail(ad),
#              # author="Santiago L. Valdarrama",
#              # guid=Guid("http://www.example.com/articles/1"),
#              pubDate=ad.parse_date,
#              )
#       items.append(item)
#    print(prov.get_raw("https://www.olx.ua/d/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/uzhgorod/"))    
    with RequestsSession() as session:
        ads = fetch_ads(session)
        #print(ads)
        if ads:
            new_ads = filter_new_ads(session, ads)
    if new_ads:
        send_message_into_telegram(bot, new_ads)


if __name__ == '__main__':
    start_time = time.time()
    logger.info('=== Script has been started ===')
    try:
        main()
    except KeyboardInterrupt:
        logger.info('=== Script has been stopped manually! ===')
    except Exception as e:  # pylint: disable=broad-except
        logger.exception(e)
    else:
        logger.info('=== Script has been finished successfully ===')
    finally:
        logger.info('=== Operating time is %s seconds ===', (time.time() - start_time))
