import json
import re
from typing import Optional

from lxml import html

alwatan_labels = [
    ('السياسة', 10, 'politic'),
    ('الاقتصاد', 5, 'economy'),
    ('الرياضة', 3, 'sports'),
    ('ثقافة وفنون', 11, 'calture'),
    ('الدين الحياة', 7, 'deen'),
    ('تقنية', 9, 'technology'),
]
alwatan_labels_eng = [t[2] for t in alwatan_labels]
alwatan_labels_arab = [t[0] for t in alwatan_labels]

def check_all_labels(line: str, *args):
    from util.redis_util import getRedisClient
    cli = getRedisClient(db=14)
    json_obj = json.loads(line)

    url = json_obj.get('url')

    if not re.match(r"^\d+$", url.replace("http://alwatan.com/details/", "")):
        return None

    response = json_obj.get('response')

    dom = html.fromstring(response)

    try:
        label_node = dom.xpath("//div[@class='content']/div/a")[1]

        label_eng_word = label_node.attrib['href'].replace("http://alwatan.com/section/", "")

        cli.set(f"{label_eng_word}|{url}", 1)
    except:
        return None

# {5: 17971, 10: 17433, 3: 17155, 11: 11138, 7: 2938, 9: 39}
# /hdd/crawl_result/alwatan.com_01.json_extract_class.json
def alwatan_extractor(line: str, *args) -> Optional[str]:
    json_obj = json.loads(line)

    url = json_obj.get('url')

    if not re.match(r"^\d+$", url.replace("http://alwatan.com/details/", "")):
        return None

    response = json_obj.get('response')

    dom = html.fromstring(response)

    try:
        label_node = dom.xpath("//div[@class='content']/div/a")[1]

        label_eng_word = label_node.attrib['href'].replace("http://alwatan.com/section/", "")
        if label_eng_word not in ['front', 'opinion', 'politic', 'monaw3at']:
            return None

        # label_eng = alwatan_labels_eng.index(label_eng_word)

        # label_arab_word = label_node.text
        # label_arab = alwatan_labels_arab.index(label_arab_word)

        # if label_eng != label_arab:
        #     return None
        #
        # label = label_arab_word
        #
        # label_id = alwatan_labels[label_arab][1]

        title = dom.xpath("//article/div[@class='post-inner']/h1[@class='name post-title entry-title']/text()")[0]

        paragraphs = dom.xpath("//article/div[@class='post-inner']/div[@class='entry']/p/text()")

        paragraphs = [paragraph for paragraph in paragraphs if not re.match("^\s+$", paragraph)]

        if len(paragraphs) == 0:
            return None

    except Exception as e:
        print(e)
        return None

    return json.dumps(dict(url=url, title=title, label=label_eng_word, label_id=-1, paragraphs=paragraphs),
                      ensure_ascii=False)
