import csv
import os
from itertools import chain
from pathlib import Path
from typing import Dict

from ad.core.adapters.repository import (
    CreateAdsRepo,
    GetRepo,
    DetailedAdRepo,
    CreateAdsConfig,
    Configuration,
    Configurations,
)
from ad.core.entities import (
    BaseAds,
    BaseAd,
    FullAd,
    DetailedAd,
    DetailedAds,
    AnyAds,
    FullAds,
)
from ad.core.errors import AdapterError

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

_BASE_FILE_NAME = BASE_DIR.joinpath('.base-ads.csv')
_DETAIL_FILE_NAME = BASE_DIR.joinpath('.detail-ads.csv')
_FULL_FILE_NAME = BASE_DIR.joinpath('.full-ads.csv')

_file_field_map = {
    _BASE_FILE_NAME: BaseAd.__fields__.keys(),
    _DETAIL_FILE_NAME: DetailedAd.__fields__.keys(),
    _FULL_FILE_NAME: FullAd.__fields__.keys(),
}


def _init_storage(file_name, fields):
    if not os.path.exists(file_name):
        with open(file_name, 'w', newline='') as csvfile:
            fieldnames = fields
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()


def _migrate():
    for file_name, fields in _file_field_map.items():
        _init_storage(file_name, fields)


class CreateAdsRepoCsv(CreateAdsRepo):
    def save(self, base_ads: BaseAds) -> None:
        with open(_BASE_FILE_NAME, 'w', newline='') as csvfile:
            fieldnames = BaseAd.__fields__.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for ad in base_ads:
                writer.writerow(ad.dict())

    def get_all(self) -> BaseAds:
        with open(_BASE_FILE_NAME) as csvfile:
            reader = csv.DictReader(csvfile)
            return [BaseAd(**row) for row in reader]


class DetailedAdRepoCsv(DetailedAdRepo):
    def save(self, detailed_ad: DetailedAd) -> None:
        saved = self.get_all_detail()
        exclude_detailed = filter(lambda x: x.id != detailed_ad.id, saved)
        with open(_DETAIL_FILE_NAME, 'w', newline='') as csvfile:
            fieldnames = DetailedAd.__fields__.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for ad in chain(exclude_detailed, [detailed_ad]):
                writer.writerow(_serialize_detail(ad))

    @staticmethod
    def get_all_detail() -> DetailedAds:
        with open(_DETAIL_FILE_NAME) as csvfile:
            reader = csv.DictReader(csvfile)
            return [_deserialize_detail(row) for row in reader]

    @staticmethod
    def get_all_base() -> BaseAds:
        return CreateAdsRepoCsv().get_all()

    def get_base_ad_by_id(self, id: str) -> BaseAd:
        try:
            return [x for x in self.get_all_base() if x.id == id][0]
        except IndexError:
            raise AdapterError(f'Не найдено объявление {id}')


def _serialize_detail(ad: DetailedAd) -> Dict:
    data = ad.dict()
    urls = _serialize_urls(data.pop('image_urls'))
    data['image_urls'] = urls
    return data


def _deserialize_detail(row: Dict) -> DetailedAd:
    raw = row.pop('image_urls')
    urls = _deserialize_urls(raw)
    row['image_urls'] = urls
    return DetailedAd(**row)


def _serialize_urls(urls):
    return ','.join(urls)


def _deserialize_urls(raw: str):
    if not raw:
        return []
    return raw.split(',')


class GetBaseAdRepoCsv(GetRepo):
    def get_all(self) -> BaseAds:
        return CreateAdsRepoCsv().get_all()

    def get_by_tag(self, tag: str) -> BaseAds:
        return _filter_by_tag(tag, self.get_all())


class DetailedAdGetRepoCsv(GetRepo):
    def get_all(self) -> DetailedAds:
        return DetailedAdRepoCsv().get_all_detail()

    def get_by_tag(self, tag: str) -> DetailedAds:
        return _filter_by_tag(tag, self.get_all())


def _filter_by_tag(tag, items: AnyAds) -> AnyAds:
    return [ad for ad in items if ad.tag == tag]


class CreateAdsConfigJson(CreateAdsConfig):
    def get_configuration(self) -> Configurations:
        return Configuration.parse_file('configuration.json').__root__


class GetDebugRepo(GetRepo):
    def get_all(self) -> FullAds:
        ad = FullAd(
            id='bc516e2abb5445ae9d03128a7a911f8f',  # dont show in template
            tag='arenda-dnepr',  # dont show in template
            title='Сдам 2-х комнатную квартиру на длительный период - Днепр',
            publication_date='2021-11-04 12:58:45',  # dont show in template
            parse_date='2021-11-04 12:58:45',
            url='https://www.olx.ua/d/obyavlenie/sdam-2-h-komnatnuyu-kvartiru-na-dlitelnyy-period-IDN7dzO.html',
            description='Сдам 2-х комнатную квартиру на длительный период для семейной пары в районе '
            '97 школы'
            ' (Ул. Братьев Трофимовых 40), 6 этаж 9-и этажного дома, не угловая, теплая, есть лоджия, застеклена.',
            image_urls=[
                'https://ireland.apollo.olxcdn.com:443/v1/files/dodwyas1emy32-UA/image;s=4000x3000',
                'https://ireland.apollo.olxcdn.com/v1/files/pxokmbrmwf9v2-UA/image;s=1104x1472',
                'https://ireland.apollo.olxcdn.com/v1/files/ve9s1d20cn211-UA/image;s=1104x1472',
                'https://ireland.apollo.olxcdn.com/v1/files/ralzthng8yp52-UA/image;s=1944x2592',
                'https://ireland.apollo.olxcdn.com/v1/files/il2y84fnyo5w-UA/image;s=591x1280',
            ],
            external_id='725276749',
            name='Феликс',
            phone='+380995437751',
        )
        return [ad]

    def get_by_tag(self, tag: str) -> DetailedAds:
        return _filter_by_tag(tag, self.get_all())


if __name__ == '__main__':
    _migrate()
