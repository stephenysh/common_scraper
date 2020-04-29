import json
import bs4
import re
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urlparse

from util.log_util import getLogger
logger = getLogger("bbc_extractor")

def extract_food(line:str, line_key: str, *args) -> Optional[str]:
    jobj = json.loads(line)
    url = jobj['url']
    url_parsed = urlparse(url)

    try:
        label_id = 0

        response = jobj['response']
        soup = BeautifulSoup(response, 'html.parser')

        title_node = soup.select("h1.blocks-article__headline")

        if len(title_node) != 1:
            logger.error(f"no title {line_key} {url}")
            return None
        title = title_node[0].get_text()

        # **************** content ***************

        content = [n.get_text(strip=True) for n in
                   soup.select("div.blocks-article__grid p, div.blocks-article__grid h2")]

        content = [para for para in content if para != '']

        if len(content) == 0:
            logger.error(f"empty content:{line_key} {url}")
            return None

        labels = ['food&drink']
        label_id = 13


    except Exception as e:
        logger.error(f"error {e}:{line_key} {url}")
        return None


    return json.dumps(dict(url=url, title=title, content=content, source='bbc', tags=labels, label_id=label_id),
                      ensure_ascii=False)


def extract(line:str, line_key: str, *args) -> Optional[str]:
    jobj = json.loads(line)
    url = jobj['url']
    url_parsed = urlparse(url)

    if url_parsed.path.endswith('/comments'):
        return None

    try:
        label_id = 0

        response = jobj['response']
        soup = BeautifulSoup(response, 'html.parser')

        # title = soup.select("div.article-headline__text")[0].get_text()
        #
        # text_nodes = soup.select("div.article__body-content")
        if url_parsed.path.startswith('/news/topic'):
            return None
        elif url_parsed.path.startswith('/culture/') or url_parsed.path.startswith('/travel/'):
            # **************** title ***************

            title_node = soup.select("h1.primary-heading")

            if len(title_node) != 1:
                logger.error(f"no title {line_key} {url}")
                return None
            title = title_node[0].get_text()

            # **************** content ***************

            content = [n.get_text(strip=True) for n in soup.select("div.body-content p, div.body-content h2, div.body-content h3")]

            content = [para for para in content if para != '']

            if len(content) == 0:
                logger.error(f"empty content:{line_key} {url}")
                return None

            if url_parsed.path.startswith('/culture/'):
                labels = ['culture']
                label_id = 9
            elif url_parsed.path.startswith('/travel/'):
                labels = ['travel']
                label_id = 11
        elif url_parsed.path.startswith('/worklife/'):
            # **************** title ***************

            title_node = soup.select("div.article-headline__text")

            if len(title_node) != 1:
                logger.error(f"no title {line_key} {url}")
                return None
            title = title_node[0].get_text()

            # **************** content ***************

            content = [n.get_text(strip=True) for n in soup.select("div.body-text-card p, div.body-text-card h2, div.body-text-card h3")]

            content = [para for para in content if para != '']

            if len(content) == 0:
                logger.error(f"empty content:{line_key} {url}")
                return None

            labels = ['worklife']
            label_id = 15

        elif url_parsed.path.startswith('/news/av'):

            #**************** title ***************

            title_node = soup.select("div.vxp-media__body h1.vxp-media__headline")

            if len(title_node) != 1:
                logger.error(f"no title {line_key} {url}")
                return None
            title = title_node[0].get_text()

            #**************** content ***************

            content = [n.get_text(strip=True) for n in soup.select("div.vxp-media__summary p")]

            content = [para for para in content if para != '']

            if len(content) == 0:
                logger.error(f"empty content:{line_key} {url}")
                return None

            #**************** label ***************

            labels = []

            m = re.match(r'^/news/av/((?:\w+\-)+)\d+/[^/]+$', url_parsed.path)

            if m:
                url_label = m.group(1).split('-')[0]
                if url_label == 'magazine':
                    return None
                labels.append(url_label)

            label_node = soup.select("div[class='navigation navigation--wide'] ul.navigation-wide-list li.selected a")
            if len(label_node) == 1:
                first_label = label_node[0].get_text(strip=True).lower()
                if first_label not in labels:
                    labels.append(first_label)

            second_label_node = soup.select("div[class='secondary-navigation secondary-navigation--wide'] ul[data-panel-id='js-navigation-panel-secondary'] li.selected a")
            if len(second_label_node) == 1:
                sencond_label = second_label_node[0].get_text(strip=True).lower()
                if sencond_label not in labels:
                    labels.append(sencond_label)


            topic_list = [topic.get_text() for topic in soup.select("div#topic-tags ul.tags-list li.tags-list__tags")]
            topic_list = [topic.lower() for topic in topic_list if topic != '']
            for topic in topic_list:
                if topic not in labels:
                    labels.append(topic)

            if len(labels) == 0:
                # logger.error(f"no label node {url}")
                return None

        elif url_parsed.path.startswith('/news/'):
            #**************** title ***************
            title_node = soup.select("div.story-body h1.story-body__h1")

            if len(title_node) != 1:
                # logger.error(f"no title {url}")
                return None
            title = title_node[0].get_text()

            #**************** content ***************

            content = [n.get_text(strip=True) for n in soup.select('div.story-body__inner p, div.story-body__inner h2, div.story-body__inner h3')]
            content = [para for para in content if para != '']

            if len(content) == 0:
                logger.error(f"empty content:{line_key} {url}")
                return None

            #**************** label ***************

            labels = []

            m = re.match(r'^/news/((?:\w+\-)+)\d+(/[^/]+)?$', url_parsed.path)

            if m:
                url_label = m.group(1).split('-')[0]

                labels.append(url_label)

            label_node = soup.select("div[class='navigation navigation--wide'] ul.navigation-wide-list li.selected a")
            if len(label_node) == 1:
                first_label = label_node[0].get_text(strip=True).lower()
                if first_label not in labels:
                    labels.append(first_label)

            second_label_node = soup.select("div[class='secondary-navigation secondary-navigation--wide'] ul[data-panel-id='js-navigation-panel-secondary'] li.selected a")
            if len(second_label_node) == 1:
                sencond_label = second_label_node[0].get_text(strip=True).lower()
                if sencond_label not in labels:
                    labels.append(sencond_label)


            topic_list = [topic.get_text() for topic in soup.select("div#topic-tags ul.tags-list li.tags-list__tags")]
            topic_list = [topic.lower() for topic in topic_list if topic != '']
            for topic in topic_list:
                if topic not in labels:
                    labels.append(topic)

            if len(labels) == 0:
                logger.error(f"no label node {line_key} {url}")
                return None

        elif url_parsed.path.startswith('/sport/'):
            # **************** title ***************
            title_node = soup.select("div.story-body h1.story-body__h1")

            if len(title_node) != 1:
                # logger.error(f"no title {url}")
                return None
            title = title_node[0].get_text()

            # **************** content ***************

            content = [n.get_text(strip=True) for n in
                       soup.select('div.story-body__inner p, div.story-body__inner h2, div.story-body__inner h3')]
            content = [para for para in content if para != '']

            if len(content) == 0:
                logger.error(f"empty content:{line_key} {url}")
                return None

            # **************** label ***************

            labels = []

            m = re.match(r'^/news/((?:\w+\-)+)\d+(/[^/]+)?$', url_parsed.path)

            if m:
                url_label = m.group(1).split('-')[0]

                labels.append(url_label)

            label_node = soup.select("div[class='navigation navigation--wide'] ul.navigation-wide-list li.selected a")
            if len(label_node) == 1:
                first_label = label_node[0].get_text(strip=True).lower()
                if first_label not in labels:
                    labels.append(first_label)

            second_label_node = soup.select(
                "div[class='secondary-navigation secondary-navigation--wide'] ul[data-panel-id='js-navigation-panel-secondary'] li.selected a")
            if len(second_label_node) == 1:
                sencond_label = second_label_node[0].get_text(strip=True).lower()
                if sencond_label not in labels:
                    labels.append(sencond_label)

            topic_list = [topic.get_text() for topic in soup.select("div#topic-tags ul.tags-list li.tags-list__tags")]
            topic_list = [topic.lower() for topic in topic_list if topic != '']
            for topic in topic_list:
                if topic not in labels:
                    labels.append(topic)

            if len(labels) == 0:
                logger.error(f"no label node {line_key} {url}")
                return None
        else:
            # logger.error(f"unwant url:{line_key} {url}")
            # from util.redis_util import getRedisClient
            # cli = getRedisClient(db=2)
            # cli.set(url, 1)
            return None

    except Exception as e:
        logger.error(f"error {e}:{line_key} {url}")
        return None

    return json.dumps(dict(url=url, title=title, content=content, source='bbc', tags=labels, label_id=label_id), ensure_ascii=False)

def check_labels():
    tag2labelid = {
        'world': 0,
        'business': 3,
        'entertainment': 2,
        'technology': 4,
        'science': 4,
        'health': 14,
        'education': 6,
        'election': 5,

    }
    import json
    fr = open("/hdd/crawl_result/english_classification/crawl_www.bbc.com.json_extract.json", "rb")
    fw = open("/hdd/crawl_result/english_classification/crawl_www.bbc.com.json_extract.json_addlabel.json", "w")
    tags = []
    for line in fr:
        line = line.decode("utf-8").strip()
        if line == "":
            continue
        jobj = json.loads(line)
        tag = jobj['tags'][0]
        tags.append(tag)
        if tag in tag2labelid:
            jobj['label_id'] = tag2labelid[tag]
            fw.write(json.dumps(jobj) + '\n')
    from collections import Counter
    from pprint import pprint

    pprint(Counter(tags))
    fw.close()

from util.redis_util import getRedisClient

cli = getRedisClient(db=10)

def write_url_to_redis(line: str, *args):

    from urllib.parse import urlparse


    jobj = json.loads(line)

    url = jobj['url']
    url_parsed = urlparse(url)
    try:
        label = [p for p in url_parsed.path.split('/') if p != ''][0]
    except:
        return None
    cli.set(f"{label}|{url}", 1)

if __name__ == '__main__':
    check_labels()