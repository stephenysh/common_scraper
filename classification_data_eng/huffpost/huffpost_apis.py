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

category_labels = {'the-worldpost': (["world"], 0), 'sports': (["sports"], 1), 'entertainment': (["entertainment"], 2),
                   'business': (["business"], 3), 'science': (['science&tech', 'science'], 4),
                   'technology': (['science&tech', 'technology'], 4), 'politics': (['politics'], 5),
                   'college': (['education', 'college'], 6), 'education': (['education'], 6),
                   'relationships': (['relationships'], 7), 'women': (['relationships', 'women'], 7),
                   'divorce': (['relationships', 'divorce'], 7), 'weddings': (['relationships', 'weddings'], 7),
                   'religion': (['religion'], 8), 'arts-and-culture': (['culture'], 9), 'art': (['art&style'], 10),
                   'travel': (['travel'], 11), 'green': (['environment', 'green'], 12),
                   'environment': (['environment'], 12), 'taste': (['food&drink'], 13),
                   'health-living': (['health', 'health-living'], 14),
                   'health-and-wellness': (['health', 'health-and-wellness'], 14), 'worklife': (['worklife'], 15)}

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
        logger.warning(f"{get_cards_by_category.__name__}:{categery}:{page_id} finished with 404 response")
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
                logger.warning(f"{get_cards_by_category.__name__}:{categery}:{page_id} finished with empty result")
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
    for category in topics:
        p = Process(target=iterate_cards_by_category, args=(category,))
        p.start()
        p_list.append(p)

    for p in p_list:
        p.join()


def check_redis_huffpost():
    redis_cli = getRedisClient(db=9)

    total_labels = []
    for key in redis_cli.scan_iter():
        total_labels.append(category_labels[key.split(":")[0]])

    from collections import Counter
    from pprint import pprint
    pprint(Counter(total_labels))


def extract_from_redis():
    from bs4 import BeautifulSoup
    from tqdm import tqdm

    redis_cli = getRedisClient(db=9)

    dbsize = redis_cli.dbsize()

    fw = open("/hdd/crawl_result/english_classification/huffpost.json", 'w')
    for key in tqdm(redis_cli.scan_iter(), total=dbsize):
        value = redis_cli.get(key)

        jobj = json.loads(value)

        url = jobj['url']

        label = key.split(":")[0]
        if label not in category_labels:
            logger.error(f"unknown label: {url}")
            continue

        mytags = category_labels[label][0]
        label_id = category_labels[label][1]

        tags = mytags + jobj['tags']

        try:
            soup = BeautifulSoup(jobj['response'], 'html.parser')
            if len(soup.select("h1.headline")) == 1:

                title = soup.select("h1.headline")[0].get_text()
                # text_nodes = soup.select("section#entry-body  section[class='entry__content-list js-entry-content'] div[class='primary-cli cli cli-text']")
                text_nodes = soup.select("section#entry-body  section[class='entry__content-list js-entry-content'] p")
            elif len(soup.select("h1.headline__title")) == 1:
                title = soup.select("h1.headline__title")[0].get_text()
                # text_nodes = soup.select("div[class='entry__text js-entry-text yr-entry-text'] div[class='content-list-component yr-content-list-text text']")
                text_nodes = soup.select("div[class='entry__text js-entry-text yr-entry-text'] p")

            else:
                logger.error(f"invalid pattern: {url}")
                continue

            content = [node.get_text(strip=True) for node in text_nodes]
            content = [para for para in content if para != '' and para != 'More from HuffPost:']

            if len(content) == 0:
                logger.error(f"empty content: {url}")
                continue
        except Exception as e:
            logger.error(f"{e}: {url}")
            continue

        fw.write(
            json.dumps(dict(url=url, tags=tags, label_id=label_id, title=title, content=content, source='huffpost'),
                       ensure_ascii=False) + "\n")




if __name__ == '__main__':
    extract_from_redis()
