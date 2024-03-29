import datetime
from jinja2 import Environment, FileSystemLoader

from rfeed import Feed, Item

from ad.core.adapters import Presenter
from ad.core.entities import BaseAds, DetailedAds, FullAds, FullAd

_BASE_TEXT = 'rss from olx'


class BaseAdFeedPresenter(Presenter):
    def present(self, ads: BaseAds):
        items = []
        for ad in ads:
            item = Item(
                title=ad.title,
                link=ad.url,
                author='lerdem',
                # guid=Guid("http://www.example.com/articles/1"),
                pubDate=ad.parse_date,
            )
            items.append(item)

        description = f'{ ads[0].tag}: {_BASE_TEXT}' if ads else _BASE_TEXT
        title = ads[0].tag if ads else _BASE_TEXT
        feed = Feed(
            title=title,
            link='http://127.0.0.1/rss',
            description=description,
            language='ru-Ru',
            lastBuildDate=datetime.datetime.now(),
            items=items,
        )
        return feed.rss()


class DetailedAdFeedPresenter(Presenter):
    def present(self, ads: DetailedAds):
        items = []
        for ad in ads:
            item = Item(
                title=ad.title,
                link=ad.url,
                description=_get_detail(ad),
                author='lerdem',
                # guid=Guid("http://www.example.com/articles/1"),
                pubDate=ad.parse_date,
            )
            items.append(item)

        description = f'{ ads[0].tag}: {_BASE_TEXT}' if ads else _BASE_TEXT
        title = ads[0].tag if ads else _BASE_TEXT
        feed = Feed(
            title=title,
            link='http://127.0.0.1/rss',
            description=description,
            language='ru-Ru',
            lastBuildDate=datetime.datetime.now(),
            items=items,
        )
        return feed.rss()


class FeedDebugPresenter(Presenter):
    def present(self, ads: FullAds):
        items = []
        for ad in ads:
            item = Item(
                title=ad.title,
                link=ad.url,
                description=_get_detail(ad),
                # author="Santiago L. Valdarrama",
                # guid=Guid("http://www.example.com/articles/1"),
                pubDate=ad.parse_date,
            )
            items.append(item)

        feed = Feed(
            title='Olx Квартиры(Детали)',
            link='http://127.0.0.1/rss',
            description='This is an example of how to use rfeed to generate an RSS 2.0 feed',
            language='ru-Ru',
            lastBuildDate=datetime.datetime.now(),
            items=items,
        )
        return feed.rss()


def _get_detail(ad: FullAd) -> str:
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('description.html')
    return template.render(ad=ad)


if __name__ == '__main__':

    content = 'This is about page'

    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    template = env.get_template('description.html')

    output = template.render(preview_url=content)
    print(output)
