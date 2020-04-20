import json
import re
import urllib
from typing import Optional

from lxml import html

weetas_labels = [

]
weetas_labels_arab = [t[0] for t in weetas_labels]


def weetas_extractor(line: str) -> Optional[str]:
    json_obj = json.loads(line)

    url = json_obj.get('url')

    url_parsed = urllib.parse.urlparse(url)

    if url_parsed.netloc != "www.weetas.com":
        return None
    if url_parsed.query != '':
        return None

    path_words = [w for w in url_parsed.path.split("/") if w != '']

    response = json_obj.get('response')

    dom = html.fromstring(response)

    try:

        arab_label_word = "property"

        label_id = 8

        title = dom.xpath("//h1[@id='post-title']/text()")[0]

        paragraphs = dom.xpath("//div[@id='post-article-content']/p/text()")

        paragraphs = [paragraph for paragraph in paragraphs if not re.match("^\s+$", paragraph)]

        if len(paragraphs) == 0:
            return None

    except Exception as e:
        print(e)
        return None

    return json.dumps(dict(url=url, title=title, label=arab_label_word, label_id=label_id, paragraphs=paragraphs),
                      ensure_ascii=False)


if __name__ == '__main__':

    f = open("/hdd/crawl_result/www.weetas.com_01.json", "rb")

    for line in f:
        line = line.decode("utf-8").strip()

        res = weetas_extractor(line)
        a = 1

    # {1: 168696, 3: 165917, 2: 115931, 5: 26246, 11: 4203}
    # labels = []
    # f = open("/hdd/crawl_result/www.weetas.com_01.json_extract_class.json", "rb")
    # for line in f:
    #     line = line.decode("utf-8").strip()
    #
    #     jobj = json.loads(line)
    #     labels.append(jobj.get("label_id"))
    #
    # from collections import Counter
    # counter = Counter(labels)
    # print(counter)
