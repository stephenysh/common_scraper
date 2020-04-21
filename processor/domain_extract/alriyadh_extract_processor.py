import json
import re
import urllib
from typing import Optional

from lxml import html

alriyadh_labels = [
    ('الاقتصاد', 5, '/news.econ'),
    ('المحليات', 2, '/news.local'),
    ('أخبار المناطق', 2, '/regions'),
    ('الدولية', 1, '/news.inter'),
    ('دنيا الرياضة', 3, '/news.sport'),
    ('ثقافة اليوم', 11, '/culture'),
    ('فن', 11, '/art'),

]
alriyadh_labels_arab = [t[0] for t in alriyadh_labels]

def check_all_labls(line: str, line_key:str):
    from util.redis_util import getRedisClient
    cli = getRedisClient(db=14)

    json_obj = json.loads(line)

    url = json_obj.get('url')

    url_parsed = urllib.parse.urlparse(url)

    if url_parsed.netloc != "www.alriyadh.com":
        return None
    if url_parsed.query != '':
        return None

    path_words = [w for w in url_parsed.path.split("/") if w != '']

    if len(path_words) != 1 or not re.match(r"^\d+$", path_words[0]):
        return None

    response = json_obj.get('response')

    dom = html.fromstring(response)

    try:
        label_node = dom.xpath("//h3/ol/li[@class='active']/a")[0]

        eng_label_word = label_node.attrib['href']

        cli.set(f"{eng_label_word}|{url}", 1)
    except:
        return None


def alriyadh_extractor(line: str, *args) -> Optional[str]:
    json_obj = json.loads(line)

    url = json_obj.get('url')

    url_parsed = urllib.parse.urlparse(url)

    if url_parsed.netloc != "www.alriyadh.com":
        return None
    if url_parsed.query != '':
        return None

    path_words = [w for w in url_parsed.path.split("/") if w != '']

    if len(path_words) != 1 or not re.match(r"^\d+$", path_words[0]):
        return None

    response = json_obj.get('response')

    dom = html.fromstring(response)

    try:
        label_node = dom.xpath("//h3/ol/li[@class='active']/a")[0]

        eng_label_word = label_node.attrib['href']

        if eng_label_word not in ['/columns', '/misc', '/foll']:
            return None

        title = dom.xpath("//div[@class='article-title']/h2/text()")[0]

        paragraphs = dom.xpath("//div[@class='col-md-12 article-text']/p/text()")

        paragraphs = [paragraph for paragraph in paragraphs if not re.match("^\s+$", paragraph)]

        if len(paragraphs) == 0:
            return None

    except Exception as e:
        print(e)
        return None

    return json.dumps(dict(url=url, title=title, label=eng_label_word[1:], label_id=-1,
                           paragraphs=paragraphs), ensure_ascii=False)


if __name__ == '__main__':

    # f = open("/hdd/crawl_result/tmp.json", "rb")
    #
    # for line in f:
    #     line = line.decode("utf-8").strip()
    #
    #     res = alriyadh_extractor(line)
    #     a = 1

    # {1: 168696, 3: 165917, 2: 115931, 5: 26246, 11: 4203}
    labels = []
    f = open("/hdd/crawl_result/www.alriyadh.com_01.json_extract_class.json", "rb")
    for line in f:
        line = line.decode("utf-8").strip()

        jobj = json.loads(line)
        labels.append(jobj.get("label_id"))

    from collections import Counter

    counter = Counter(labels)
    print(counter)
