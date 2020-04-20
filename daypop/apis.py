import json

import requests

from util.log_util import getLogger
from util.redis_util import getRedisClient

logger = getLogger("daypop_apis")
categorys = ["UAE", "Arab", "World", "Entertainment", "Sport", "ScienceTechnology", "Business", "Health"]


def get_list_by_category(category: str, page: int, lang: str):
    url = f"https://api.daypop.ai/daypop/v1/channel/{category}?lang={lang}&page={page}"

    response = requests.get(url)

    assert response.status_code == 200, f"Request {get_list_by_category.__name__}:{category}:{page} Faild with code {response.status_code}"

    res = json.loads(response.text)["data"][category]

    logger.debug(f"{get_list_by_category.__name__}:{category}:{page} have list of [{len(res)}] articles")

    return res


def get_article_detail(id, lang):
    url = f"https://api.daypop.ai/daypop/v1/page/news/detail?lang={lang}&id={id}"

    response = requests.get(url)

    assert response.status_code == 200, f"Request {get_article_detail.__name__}:{id} Faild with code {response.status_code}"

    return json.loads(response.text)["data"]["detail"]


def iterate_articles_by_category(category: str):
    redis_cli = getRedisClient(db=15)

    lang = "lang"

    page_id = 0
    article_count = 0
    while True:
        page_id += 1

        try:
            article_list = get_list_by_category(category, page_id, lang)
        except Exception as e:
            logger.error(e)
            continue

        if len(article_list) == 0:
            break

        for article in article_list:
            id = article["article_id"]

            redis_key = f"{category}:{id}"

            if redis_cli.get(redis_key) is not None:
                logger.debug(f"{redis_key} found in redis")
                continue

            try:
                article_detail = get_article_detail(id, lang)
            except Exception as e:
                logger.error(e)
                continue

            redis_cli.set(redis_key, json.dumps(article_detail, ensure_ascii=False))
            article_count += 1

    logger.info(f"category {category} total articles count: {article_count}")
    return article_count


def crawl_all_articles():
    from multiprocessing import Process

    p_list = []
    for category in categorys:
        p = Process(target=iterate_articles_by_category, args=(category,))
        p.start()
        p_list.append(p)

    for p in p_list:
        p.join()


def check_redis():
    redis_cli = getRedisClient(db=15)

    total_labels = []
    for key in redis_cli.scan_iter():
        total_labels.append(key.split(":")[0])

    from collections import Counter
    from pprint import pprint
    pprint(Counter(total_labels))


if __name__ == '__main__':
    check_redis()
