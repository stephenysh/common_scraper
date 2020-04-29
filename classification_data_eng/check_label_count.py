import json
from collections import Counter
from pprint import pprint

def check_file_counter(filename):

    fr = open(filename, "rb")
    ids = []
    for line in fr:
        line = line.decode('utf-8').strip()
        if line == '':
            continue
        jobj = json.loads(line)
        ids.append(jobj['label_id'])

    pprint(sorted([(k,v) for k,v in Counter(ids).items()], key=lambda t:t[0]))


def cut_file_counter(filename):
    fr = open(filename, "rb")
    fw = open(f"{filename}_cut.json", "w")
    counter = [0] * 16
    for line in fr:
        line = line.decode('utf-8').strip()
        if line == '':
            continue
        jobj = json.loads(line)
        if len(jobj['content']) == 0:
            continue

        if counter[jobj['label_id']] >= 10000:
            continue

        fw.write(line + "\n")
        counter[jobj['label_id']] += 1


    print(counter)

def check_url_counter(filename):
    from urllib.parse import urlparse
    fr = open(filename, "rb")
    types = []
    for line in fr:
        line = line.decode('utf-8').strip()
        if line == '':
            continue
        jobj = json.loads(line)
        types.append(urlparse(jobj['url']).path.split("/")[1])

    pprint(sorted([(k,v) for k,v in Counter(types).items()], key=lambda t:t[0]))
def test():
    import urllib.parse
    base = 'https://www.example-page-xl.com'
    print(urllib.parse.urljoin(base, 'index.php'))
    print(urllib.parse.urljoin(base, '../index.php'))
    print(urllib.parse.urljoin(base, '/helloworld/index.php'))
    print(urllib.parse.urljoin(base, '//helloworld/index.php'))
    print(urllib.parse.urljoin(base, 'https://www.example-page-xl.com/helloworld/index.php'))

from util.redis_util import getRedisClient
deduplicate_redis_cli = getRedisClient(db=15)
import json
def redis_deduplicate(line: str, line_key:str):
    jobj = json.loads(line)
    if deduplicate_redis_cli.get(jobj['url']) is None:
        deduplicate_redis_cli.set(jobj['url'], 1)
        return line

    else:
        return None


if __name__ == '__main__':
    # test()
    # [(0, 24639),
    #  (1, 14368),
    #  (2, 1287),
    #  (3, 2300),
    #  (4, 1659),
    #  (5, 13448),
    #  (6, 308),
    #  (11, 81),
    #  (12, 145),
    #  (13, 2),
    #  (14, 6267),
    #  (15, 401)]
    # check_file_counter('/hdd/crawl_result/english_classification/crawl_edition.cnn.com_01.json_extract.json')

    # [(0, 158),
    #  (1, 22),
    #  (2, 279),
    #  (3, 73),
    #  (4, 99),
    #  (5, 343),
    #  (6, 1482),
    #  (7, 16296),
    #  (8, 2301),
    #  (9, 61),
    #  (10, 14395),
    #  (11, 101),
    #  (12, 21356),
    #  (13, 119),
    #  (14, 14319),
    #  (15, 64)]
    # check_file_counter('/hdd/crawl_result/english_classification/huffpost.json_extract.json')



    #  0 World News             [(0, 65856),           [(0, 65856),
    #  1 Sports                  (1, 14390),            (1, 14390),
    #  2 Entertainment           (2, 11936),            (2, 11936),
    #  3 Business                (3, 16176),            (3, 16176),
    #  4 Science and Tech        (4, 11689),            (4, 11689),
    #  5 Politics                (5, 15156),            (5, 15156),
    #  6 Education               (6, 3950), *           (6, 3950),
    #  7 Relationship            (7, 16296),            (7, 16296),
    #  8 Religions               (8, 2301), *           (8, 2301),
    #  9 Cultures                (9, 61),               (9, 11670),
    #  10 Arts & style           (10, 14395),           (10, 14395),
    #  11 Travel                 (11, 182),             (11, 15980),
    #  12 Environment            (12, 21501),           (12, 21501),
    #  13 Food & Drink           (13, 121), *           (13, 121),
    #  14 Health                 (14, 25429),           (14, 25429),
    #  15 Worklife               (15, 465)] *           (15, 1855)]
    # check_file_counter('/hdd/crawl_result/english_classification/result.json')

    check_file_counter('/hdd/crawl_result/english_classification/eng_cls_all.json')

    # check_file_counter('/hdd/crawl_result/english_classification/crawl_www.bbc.com.json_extract.json_addlabel.json')