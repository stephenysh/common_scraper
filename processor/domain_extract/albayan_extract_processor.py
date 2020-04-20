import json
import re
import urllib
from typing import Optional

from lxml import html

from processor.domain_extract.alriyadh_extract_processor import alriyadh_extractor

labels = {'1!': '世界:1316', '2!': '中东', '3!': '体育', '4:375': '健康', '5!': '商业经济',
          '6': '妇女', '7:3000': '宗教生活', '8': '房地产', '9:181': '技术科学', '10!': '政治',
          '11!': '文化文艺', '12': '旅游', '13': '汽车', '14': '法律', '15': '环境'}

# https://www.albayan.ae/	阿联酋、世界、经济、体育、观点*、艺术、健康、科技
# http://alwatan.com/	政治、经济、体育、观点*、文艺、宗教生活、科技
# https://arabic.rt.com/	经济、体育、科技、健康、文艺、法律、数据、汽车、房地产
# https://alwafd.news/	体育、经济、世界、艺术


# {2: 2115, 1: 1316, 11: 1289, 3: 870, 5: 839, 4: 375, 9: 181}
# /hdd/crawl_result/www.albayan.ae_01.json_extract_class.json
albayan_labels = [
    ('الرياضي', 3, 'sports'),
    ('عبر الإمارات', 2, 'across-the-uae'),
    ('عالم واحد', 1, 'one-world'),
    ('الاقتصادي', 5, 'economy'),
    ('فكر وفن', 11, 'five-senses'),
    ('الكتب', 11, 'books'),
    ('البيان الصحي', 4, 'health'),
    ('التقنية', 9, 'technology'),

]
albayan_labels_eng = [t[2] for t in albayan_labels]
albayan_labels_arab = [t[0] for t in albayan_labels]


def albayan_extractor(line: str) -> Optional[str]:
    json_obj = json.loads(line)

    url = json_obj.get('url')

    url_parsed = urllib.parse.urlparse(url)

    if url_parsed.netloc != "www.albayan.ae":
        return None
    if url_parsed.query != '':
        return None

    path_words = [w for w in url_parsed.path.split("/") if w != '']

    if not re.match(r"^[\d\.\-]+$", path_words[-1]):
        return None

    label_eng_word = path_words[0]

    if label_eng_word not in albayan_labels_eng:
        return None

    response = json_obj.get('response')

    dom = html.fromstring(response)

    try:
        label_arab_word = dom.xpath(f"//section[@class='row']//a[@href='/{label_eng_word}']//text()")[0]

        label_eng = albayan_labels_eng.index(label_eng_word)

        label_arab = albayan_labels_arab.index(label_arab_word)

        if label_eng != label_arab:
            return None

        label = label_arab_word

        label_id = albayan_labels[label_arab][1]

        title = dom.xpath("//h1[@class='title']/text()")[0]

        paragraphs = dom.xpath("//div[@id='articledetails']//p/text()")

        if len(paragraphs) == 0:
            paragraphs = dom.xpath("//div[@id='articledetails']/div[2]//text()")
            paragraphs = [paragraph for paragraph in paragraphs if
                          len(paragraph) > 3 and not re.match(r"^\s+$", paragraph)]

        if len(paragraphs) == 0:
            return None

    except Exception as e:
        print(e)
        return None

    return json.dumps(dict(url=url, title=title, label=label, label_id=label_id, paragraphs=paragraphs),
                      ensure_ascii=False)


if __name__ == '__main__':

    f = open("/hdd/crawl_result/tmp.json", "rb")

    for line in f:
        line = line.decode("utf-8").strip()

        res = alriyadh_extractor(line)
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
