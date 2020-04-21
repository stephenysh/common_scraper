import json
import re
import urllib
from typing import Optional

from lxml import html

# {'/middle_east/': 11851, '/world/': 10161, '/sport/': 2697, '/health/': 2599, '/russia/': 2512, '/business/': 2257, '/technology/': 2047, '/space/': 1518, '/culture/': 1193, '/funny/': 1119, '/videoclub/': 1038, '/it/': 953, '/society/': 914, '/press/': 639, '/car/': 540, '': 155, '/info/': 87, '/victory-world-war-II/': 54})

labels = {'1!': '世界:1316', '2!': '中东', '3!': '体育', '4:3000': '健康', '5!': '商业经济',
          '6': '妇女', '7:3000': '宗教生活', '8': '房地产', '9!': '技术科学', '10!': '政治',
          '11!': '文化文艺', '12': '旅游', '13:540': '汽车', '14': '法律', '15': '环境'}

arabicrt_labels = {
    '/middle_east/': 2,
    '/world/': 1,
    '/sport/': 3,
    '/health/': 4,
    '/business/': 5,
    '/technology/': 9,
    '/space/': 9,
    '/it/': 9,
    '/culture/': 11,
    '/car/': 13

}
def check_all_labels(line: str, line_key:str):
        from util.redis_util import getRedisClient
        redis_cli = getRedisClient(db=14)

        json_obj = json.loads(line)

        url = json_obj.get('url')

        url_parsed = urllib.parse.urlparse(url)

        if url_parsed.netloc != "arabic.rt.com":
            return None
        if url_parsed.query != '':
            return None

        path_words = [w for w in url_parsed.path.split("/") if w != '']

        if len(path_words) != 2:
            return None

        response = json_obj.get('response')

        dom = html.fromstring(response)

        try:

            labrel_node = dom.xpath(f"//div[@class='info-panel']//a[@href]")[0]

            href_label = labrel_node.attrib['href']

            redis_cli.set(f"{href_label}|{url}", 1)
        except:
            return None

def arabicrt_extractor(line: str, *args) -> Optional[str]:
    json_obj = json.loads(line)

    url = json_obj.get('url')

    url_parsed = urllib.parse.urlparse(url)

    if url_parsed.netloc != "arabic.rt.com":
        return None
    if url_parsed.query != '':
        return None

    path_words = [w for w in url_parsed.path.split("/") if w != '']

    if len(path_words) != 2:
        return None

    response = json_obj.get('response')

    dom = html.fromstring(response)

    try:
        url_label = path_words[0]

        labrel_node = dom.xpath(f"//div[@class='info-panel']//a[@href]")[0]

        href_label = labrel_node.attrib['href']

        if href_label not in ['/russia/', '/space/', '/funny/', '/society/', '/press/', 'victory-world-war-II']:
            return None

        # arab_label_word = labrel_node.text
        #
        # label_id = arabicrt_labels[href_label]

        title = dom.xpath("//h1[@class='heading']/text()")[0]

        paragraphs = dom.xpath("//div[@class='article ']//p/text()")

        paragraphs = [paragraph for paragraph in paragraphs if not re.match("^\s+$", paragraph)]

        if len(paragraphs) == 0:
            return None

    except Exception as e:
        print(e)
        return None

    return json.dumps(
        dict(url=url, title=title, label=href_label[1:-1], label_id=-1,
             paragraphs=paragraphs), ensure_ascii=False)


if __name__ == '__main__':

    # f = open("/hdd/crawl_result/tmp.json", "rb")
    #
    # for line in f:
    #     line = line.decode("utf-8").strip()
    #
    #     res = arabicrt_extractor(line)
    #     a = 1

    # {2: 11851, 1: 10161, 9: 4518, 3: 2697, 4: 2599, 5: 2257, 11: 1193, 13: 540}
    # labels = []
    # f = open("/hdd/crawl_result/arabic.rt.com_01.json_extract_class.json", "rb")
    # for line in f:
    #     line = line.decode("utf-8").strip()
    #
    #     jobj = json.loads(line)
    #     labels.append(jobj.get("label_id"))
    #
    # from collections import Counter
    #
    # counter = Counter(labels)
    # print(counter)

    check_all_labels()