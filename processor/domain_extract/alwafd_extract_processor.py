import json
import re
import urllib
from typing import Optional

from lxml import html

alwafd_labels = [
    ('الاقتصاد', 5, '/news.econ'),
    ('المحليات', 2, '/news.local'),
    ('أخبار المناطق', 2, '/regions'),
    ('الدولية', 1, '/news.inter'),
    ('دنيا الرياضة', 3, '/news.sport'),
    ('ثقافة اليوم', 11, '/culture'),
    ('فن', 11, '/art'),

]
alwafd_labels_arab = [t[0] for t in alwafd_labels]


def alwafd_extractor(line: str) -> Optional[str]:
    json_obj = json.loads(line)

    url = json_obj.get('url')

    url_parsed = urllib.parse.urlparse(url)

    if url_parsed.netloc != "www.alwafd.com":
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

        arab_label_word = label_node.text
        eng_label_word = label_node.attrib['href']

        if arab_label_word not in alwafd_labels_arab:
            return None

        arab_label = alwafd_labels_arab.index(arab_label_word)

        label_id = alwafd_labels[arab_label][1]

        title = dom.xpath("//div[@class='article-title']/h2/text()")[0]

        paragraphs = dom.xpath("//div[@class='col-md-12 article-text']/p/text()")

        paragraphs = [paragraph for paragraph in paragraphs if not re.match("^\s+$", paragraph)]

        if len(paragraphs) == 0:
            return None

    except Exception as e:
        print(e)
        return None

    return json.dumps(dict(url=url, title=title, label=arab_label_word, eng_label=eng_label_word, label_id=label_id,
                           paragraphs=paragraphs), ensure_ascii=False)


if __name__ == '__main__':

    f = open("/hdd/crawl_result/tmp.json", "rb")

    for line in f:
        line = line.decode("utf-8").strip()

        res = alwafd_extractor(line)
        a = 1

    # labels = []
    # f = open("/hdd/crawl_result/www.albayan.ae_01.json_extract_class.json", "rb")
    # for line in f:
    #     line = line.decode("utf-8").strip()
    #
    #     jobj = json.loads(line)
    #     labels.append(jobj.get("label_id"))
    #
    # from collections import Counter
    # counter = Counter(labels)
    # print(counter)
