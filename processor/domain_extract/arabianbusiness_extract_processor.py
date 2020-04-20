import json
import re
import urllib
from typing import Optional

from lxml import html

arabianbusiness_labels = [

]
arabianbusiness_labels_arab = [t[0] for t in arabianbusiness_labels]


def arabianbusiness_extractor(line: str) -> Optional[str]:
    json_obj = json.loads(line)

    url = json_obj.get('url')

    url_parsed = urllib.parse.urlparse(url)

    if url_parsed.netloc != "arabic.arabianbusiness.com":
        return None
    if url_parsed.query != '':
        return None

    path_words = [w for w in url_parsed.path.split("/") if w != '']

    if len(path_words) != 2 and path_words[0] != 'real-estate':
        return None

    response = json_obj.get('response')

    dom = html.fromstring(response)

    try:

        arab_label_word = "property"

        label_id = 8

        title = dom.xpath("//h1[@class='news-title change-font-size']/text()")[0]

        paragraphs = dom.xpath("//div[@class='news-body-data change-font-size']/p/text()")

        paragraphs = [paragraph for paragraph in paragraphs if not re.match("^\s+$", paragraph)]

        if len(paragraphs) == 0:
            return None

    except Exception as e:
        print(e)
        return None

    return json.dumps(dict(url=url, title=title, label=arab_label_word, label_id=label_id, paragraphs=paragraphs),
                      ensure_ascii=False)


if __name__ == '__main__':

    f = open("/hdd/crawl_result/arabic.arabianbusiness.com_01.json", "rb")

    for line in f:
        line = line.decode("utf-8").strip()

        res = arabianbusiness_extractor(line)
        a = 1

    # {1: 168696, 3: 165917, 2: 115931, 5: 26246, 11: 4203}
    # labels = []
    # f = open("/hdd/crawl_result/www.arabianbusiness.com_01.json_extract_class.json", "rb")
    # for line in f:
    #     line = line.decode("utf-8").strip()
    #
    #     jobj = json.loads(line)
    #     labels.append(jobj.get("label_id"))
    #
    # from collections import Counter
    # counter = Counter(labels)
    # print(counter)
