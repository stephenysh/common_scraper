import json
import re
import urllib
from typing import Optional

from bs4 import BeautifulSoup
from lxml import html

# {'/middle_east/': 11851, '/world/': 10161, '/sport/': 2697, '/health/': 2599, '/russia/': 2512, '/business/': 2257, '/technology/': 2047, '/space/': 1518, '/culture/': 1193, '/funny/': 1119, '/videoclub/': 1038, '/it/': 953, '/society/': 914, '/press/': 639, '/car/': 540, '': 155, '/info/': 87, '/victory-world-war-II/': 54})

labels = {'1!': '世界:1316', '2!': '中东', '3!': '体育', '4:3000': '健康', '5!': '商业经济',
          '6': '妇女', '7:3000': '宗教生活', '8': '房地产', '9!': '技术科学', '10!': '政治',
          '11!': '文化文艺', '12': '旅游', '13:540': '汽车', '14': '法律', '15': '环境'}

unnews_labels = {
    '/ar/news/topic/climate-change': 15,
    '/ar/news/topic/women': 6,
}


def unnews_extractor(line: str) -> Optional[str]:
    json_obj = json.loads(line)

    url = json_obj.get('url')

    url_parsed = urllib.parse.urlparse(url)

    if url_parsed.netloc != "news.un.org":
        return None
    if url_parsed.query != '':
        return None

    if not re.match("^/ar/story/\d+/\d+/\d+$", url_parsed.path):
        return None

    response = json_obj.get('response')

    dom = html.fromstring(response)

    try:

        label_node = dom.xpath("((//div[@class='content'])[1]//a)[1]")

        if len(label_node) == 0:
            return None
        label_node = label_node[0]

        arab_label = label_node.text
        if arab_label is None:
            return None

        eng_label = label_node.attrib['href']
        if eng_label not in unnews_labels:
            return None

        label_id = unnews_labels[eng_label]

        title = dom.xpath("//h1[@class='story-title']/text()")[0]

        paragraphs = [p.get_text() for p in BeautifulSoup(response).select("div[class='content']:nth-of-type(1) p")]

        paragraphs = [paragraph for paragraph in paragraphs if not re.match("^\s+$", paragraph)]

        if len(paragraphs) == 0:
            return None

    except Exception as e:
        print(e)
        return None

    return json.dumps(dict(url=url, title=title, eng_label=eng_label, arab_label=arab_label, label_id=label_id,
                           paragraphs=paragraphs), ensure_ascii=False)


if __name__ == '__main__':

    # f = open("/hdd/crawl_result/tmp.json", "rb")
    #
    # for line in f:
    #     line = line.decode("utf-8").strip()
    #
    #     res = unnews_extractor(line)
    #     a = 1

    # {2: 11851, 1: 10161, 9: 4518, 3: 2697, 4: 2599, 5: 2257, 11: 1193, 13: 540}
    labels = []
    f = open("/hdd/crawl_result/news.un.org_01.json_extract_class.json", "rb")
    for line in f:
        line = line.decode("utf-8").strip()

        jobj = json.loads(line)
        labels.append(jobj.get("eng_label"))

    from collections import Counter

    counter = Counter(labels)
    print(counter)
