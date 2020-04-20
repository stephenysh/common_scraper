import json
import re
import time

import requests

from util.log_util import getLogger
from util.redis_util import getRedisClient

logger = getLogger("huffpost_apis")

headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363'
}

sections = ['sports', 'entertainment', 'business', 'science', 'technology', 'relationships', 'women', 'religion',
            'travel', 'green', 'taste']

topics = ['the-worldpost', 'politics', 'college', 'education', 'divorce', 'weddings', 'arts-and-culture', 'art',
          'environment', 'health-living', 'health-and-wellness', 'worklife']


def get_cards_by_category(categery: str, page_id: int):
    time.sleep(1)
    if categery in sections:
        topic_or_section = "section"
    elif categery in topics:
        topic_or_section = "topic"
    else:
        raise RuntimeError("invalid categery")

    url = f"https://www.huffpost.com/api/{topic_or_section}/{categery}/cards?page={page_id}&limit=undefined"

    response = requests.get(url, headers=headers)

    if response.status_code == 404:
        logger.warning(f"{get_cards_by_category.__name__}:{categery}:{page_id} finished")
        return []

    assert response.status_code == 200, f"{get_cards_by_category.__name__}:{categery}:{page_id} failed with status code {response.status_code}"

    cards = []

    for card in json.loads(response.text)['cards']:

        if len(card['headlines']) != 1:
            continue

        d = card['headlines'][0]

        url = d['url']

        if not re.match(r"https://www\.huffpost\.com/entry/[\w_-]+", url):
            continue

        entry_id = d['entry_id']

        title = d['text']

        tags = d['tags']

        cards.append(dict(url=url, id=entry_id, title=title, tags=tags))

    return cards


def iterate_cards_by_category(categery: str):
    time.sleep(1)

    redis_cli = getRedisClient(db=9)

    page_id = 0
    while True:

        try:

            cards = get_cards_by_category(categery, page_id)

            if len(cards) == 0:
                break

            for card in cards:

                url = card['url']

                redis_key = f"{categery}:{url}"

                if redis_cli.get(redis_key) is not None:
                    continue

                response = requests.get(url, headers=headers)

                card['response'] = response.text

                redis_cli.set(redis_key, json.dumps(card))

        except Exception as e:
            logger.error(e)

        page_id += 1


def crawl_all_huffpost():
    from multiprocessing import Process

    p_list = []
    for category in sections + topics:
        p = Process(target=iterate_cards_by_category, args=(category,))
        p.start()
        p_list.append(p)

    for p in p_list:
        p.join()


def check_redis():
    redis_cli = getRedisClient(db=9)

    total_labels = []
    for key in redis_cli.scan_iter():
        total_labels.append(key.split(":")[0])

    from collections import Counter
    from pprint import pprint
    pprint(Counter(total_labels))


if __name__ == '__main__':
    crawl_all_huffpost()
