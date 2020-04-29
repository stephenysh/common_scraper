import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Optional
from util.log_util import getLogger

logger = getLogger("guardian")

culture_sencond_level_labels = ["books", "music", "tv-and-radio", "artanddesign", "film", "games", "stage"]
food_sencond_level_labels = ["food"]
travel_sencond_level_labels = ["travel"]
travel_sencond_level_labels = ["travel"]
def extract(line: str, line_key:str, *args) -> Optional[str]:
    jobj = json.loads(line)

    url = jobj['url']
    url_parsed = urlparse(url)

    if url_parsed.netloc != "www.theguardian.com":
        print(f"{line_key} {jobj['url']} error: invalid netloc")
        return None

    # sencond_level_label = [p for p in url_parsed.path.split('/') if p != ''][0]
    #
    # if sencond_level_label not in food_sencond_level_labels:
    #     print(f"{line_key} {jobj['url']} error: unknown label")
    #     return None

    #
    # tags = ['religion']
    # label_id = 8
    #
    # tags = ['travel']
    # label_id = 11

    # tags = ['food']
    # label_id = 13

    tags = ['education']
    label_id = 6

    try:
        soup = BeautifulSoup(jobj['response'], 'html.parser')
        title = soup.select("h1.content__headline ")[0].get_text()
        content = [n.get_text() for n in soup.select('div[data-test-id="article-review-body"] > p')]
        content = [text for text in content if text != '']
        assert len(content) > 0, "empty content"

    except Exception as e:
        print(f"{line_key} {jobj['url']} error: {e}")
        return None

    return json.dumps(dict(url=jobj['url'], tags=tags, label_id=label_id, title=title, content=content), ensure_ascii=False)

def request(topic):
    topic_label = {"religion": "world/religion"}

    import requests

    fw = open(f'/hdd/crawl_result/english_classification/basic_guardian_spider_{topic}.json', 'w')
    page_id = 1

    while True:
        if page_id > 10000:
            break
        try:
            if topic in topic_label:
                page_url = f'https://www.theguardian.com/{topic_label[topic]}?page={page_id}'
            else:
                page_url = f'https://www.theguardian.com/{topic}?page={page_id}'

            page_response = requests.get(page_url)

            assert page_response.status_code == 200, "invalid response"

            logger.info(page_url)

            soup = BeautifulSoup(page_response.text, 'html.parser')

            for node in soup.select('div[class="fc-item__content"] a'):
                try:
                    title = node.text

                    url = node.attrs['href']

                    response = requests.get(url)

                    assert response.status_code == 200, "invalid response"

                    fw.write(json.dumps(dict(title=title, url=url, response=response.text), ensure_ascii=False) + '\n')
                except:
                    continue

        except:
            continue
        page_id += 1

def add_source():
    fr = open("/hdd/crawl_result/english_classification/guardian.json", "rb")
    fw = open("/hdd/crawl_result/english_classification/guardian.json_addsource.json", "w")

    for line in fr:
        line = line.decode("utf-8")
        jobj = json.loads(line)
        jobj['source']='theguardian'
        fw.write(json.dumps(jobj, ensure_ascii=False) + "\n")

if __name__ == '__main__':
    add_source()
