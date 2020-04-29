from util.log_util import getLogger
import re
import json
from bs4 import BeautifulSoup
from lxml import html

from urllib.parse import urlparse
from typing import Optional
labels = {
'africa': (["world", "africa"], 0),
'africa_gallery': (["world", "africa"], 0),
'americas': (["world", "americas"], 0),
'americas_gallery': (["world", "americas"], 0),
'asia': (["world", "asia"], 0),
'asia_gallery': (["world", "asia"], 0),
'australia': (["world", "australia"], 0),
'business': (["business"], 3),
'business_gallery': (["business"], 3),
'cars': (["travel"], 11),
'celebrities': (["entertainment"], 2),
'china': (["world", "china"], 0),
'china_gallery': (["world", "china"], 0),
'economy': (["business"], 3),
'energy': (["environment"], 12),
'entertainment': (["entertainment"], 2),
'entertainment_gallery': (["entertainment"], 2),
'europe': (["world", "europe"], 0),
'europe_gallery': (["world", "europe"], 0),
'foodanddrink': (["food&drink"], 13),
'football': (["sports", "football"], 1),
'football_gallery': (["sports", "football"], 1),
'golf': (["sports", "golf"], 1),
'golf_gallery': (["sports", "golf"], 1),
'health': (["health"], 14),
'health_conditions': (["health"], 14),
'health_diet-fitness': (["health"], 14),
'health_gallery': (["health"], 14),
'health_living-well': (["health"], 14),
'health_mental-health': (["health"], 14),
'india': ( ["world", "india"], 0),
'india_gallery': (["world", "india"], 0),
'investing': (["business"], 3),
'justice': (["politics"], 5),
'justice_gallery': (["politics"], 5),
'living': (["worklife"], 15),
'living_gallery': (["worklife"], 15),
'middleeast': (["world", "middleeast"], 0),
'middleeast_gallery': (["world", "middleeast"], 0),
'motorsport': (["sports", "motorsport"], 1),
'motorsport_gallery': (["sports", "motorsport"], 1),
'politics': (["politics"], 5),
'politics_gallery': (["politics"], 5),
'sailing': (["sports", "sailing"], 1),
'sailing_gallery': (["sports", "sailing"], 1),
'showbiz': (["entertainment"], 2),
'showbiz_celebrity-news-gossip': (["entertainment"], 2),
'showbiz_gallery': (["entertainment"], 2),
'showbiz_movies': (["entertainment"], 2),
'showbiz_music': (["entertainment"], 2),
'showbiz_tv': (["entertainment"], 2),
'skiing': (["sports", "skiing"], 1),
'skiing_gallery': (["sports", "skiing"], 1),
'sport': (["sports"], 1),
'sport_football': (["sports", "football"], 1),
'sport_gallery': (["sports"], 1),
'sport_golf': (["sports", "golf"], 1),
'sport_motorsport': (["sports", "motorsport"], 1),
'sport_tennis': (["sports", "tennis"], 1),
'studentnews': (["education"], 6),
'success': (["education"], 6),
'tech': (["science&tech"], 4),
'tech_gallery': (["science&tech"], 4),
'tech_gaming-gadgets': (["science&tech"], 4),
'tech_innovation': (["science&tech"], 4),
'tech_mobile': (["science&tech"], 4),
'tech_social-media': (["science&tech"], 4),
'tech_web': (["science&tech"], 4),
'technology': (["science&tech"], 4),
'tennis': (["sports", "tennis"], 1),
'tennis_gallery': (["sports", "tennis"], 1),
'travel': (["travel"], 11),
'tv': (["entertainment"], 2),
'tv-shows': (["entertainment"], 2),
'uk': (["world", "uk"], 0),
'uk_gallery': (["world", "uk"], 0),
'us': (["world", "us"], 0),
'us_gallery': (["world", "us"], 0),
'vr': (["science&tech"], 4),
'weather': (["environment"], 12),
'weather_gallery': (["environment"], 12),
'world': (["world"], 0),
'world_africa': (["world", "africa"], 0),
'world_americas': (["world", "americas"], 0),
'world_asia': (["world", "asia"], 0),
'world_europe': (["world", "europe"], 0),
'world_gallery': (["world"], 0),
'world_meast': (["world", "middleeast"], 0),
'worldsport_gallery': (["sports"], 0),
}

def extract(line: str, line_key:str, *args) -> Optional[str]:
    jobj = json.loads(line)

    url = jobj['url']
    url_parsed = urlparse(url)

    if url_parsed.netloc != "edition.cnn.com":
        print(url)
        return None

    m = re.match("^(/\d+){3}((?:/[^/]+)+)/index\.html$", url_parsed.path)

    if m is None:
        print(url)

        return None

    path_parts = [p for p in m.group(2).split("/") if p != '']

    if len(path_parts) <= 1:
        print(url)
        return None
    label = "_".join(path_parts[:-1])

    if label not in labels:
        return None
    tags = labels[label][0]
    label_id = labels[label][1]

    try:
        soup = BeautifulSoup(jobj['response'], 'html.parser')
        title = soup.select("h1.pg-headline")[0].get_text()
        content = [n.get_text() for n in soup.select('section#body-text [class^="zn-body__paragraph"]')]
        content = [text for text in content if text != '']
        assert len(content) > 0, "empty content"

    except Exception as e:
        print(f"{line_key} {jobj['url']} error: {e}")
        return None

    return json.dumps(dict(url=jobj['url'], tags=tags, label_id=label_id, title=title, content=content), ensure_ascii=False)

def write_url_to_redis(line: str, *args):
    from util.redis_util import getRedisClient
    cli = getRedisClient(db=8)

    jobj = json.loads(line)

    url = jobj['url']
    url_parsed = urlparse(url)

    if url_parsed.netloc != "edition.cnn.com":
        print(url)
        return None

    m = re.match("^(/\d+){3}((?:/[^/]+)+)/index\.html$", url_parsed.path)

    if m is None:
        print(url)

        return None

    path_parts = [p for p in m.group(2).split("/") if p != '']

    if len(path_parts) <= 1:
        print(url)

        return None
    label = "_".join(path_parts[:-1])
    cli.set(f"{label}|{url}", 1)

if __name__ == '__main__':
    logger = getLogger("cnn")

    fw = open("/hdd/crawl_result/english_classification/crawl_edition.cnn.com_01.json_extract.json.json", "w")

    with open("/hdd/crawl_result/english_classification/crawl_edition.cnn.com_01.json_extract.json", "rb") as fr:
        for lineno, line in enumerate(fr):
            line = line.decode("utf-8").strip()
            jobj = json.loads(line)
            jobj['source'] = 'cnn'
            t = jobj['content'][0]
            jobj['content'][0] = re.sub("\(CNN ?\w*\)", lambda m: m.group(0)+' ',t)

            fw.write(json.dumps(jobj) + '\n')


