import time
import requests
from scrapy import Selector

headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363'
    }

def get_news(news_url, prefix):
    s = requests.Session()
    s.keep_alive = False  # 关闭多余连接
    repeat = 10
    while repeat:
        try:
            resp = s.get(news_url, headers=headers, verify=False, timeout=20)
            break
        except:
            print('trying:', repeat)
            repeat -= 1
            time.sleep(3)
    if repeat == 0:
        return
    resp.encoding = 'UTF-8'
    sel = Selector(resp)
    title = sel.xpath('//*[@id="article_content"]/h2/text()').extract_first()
    contents = sel.xpath('//*[@id="article_content"]/div[@class="node_new_body"]/text()').extract()
    content = "\n".join(contents) if contents else ""
    target_file = 'aawsat/' + prefix + '.txt'
    print(news_url)
    print(title)
    print("==================")
    with open(target_file, 'a', encoding='utf-8') as t:
        if title:
            t.write(title)
            t.write('\n')
        if content:
            t.write(content)
            t.write('\n')
    now_day = time.strftime("%Y-%m-%d", time.localtime())
    target_file = 'aawsat/' + 'count_' + now_day + '.txt'
    with open(target_file, 'a', encoding='utf-8') as t:
        if content:
            t.write(news_url)
            t.write('\n')

def get_urls(url):
    s = requests.Session()
    s.keep_alive = False  # 关闭多余连接
    repeat = 10
    while repeat:
        try:
            resp = s.get(url, headers=headers, verify=False, timeout=20)
            break
        except:
            print('trying:', repeat)
            repeat -= 1
            time.sleep(3)
    if repeat == 0:
        return
    resp.encoding='UTF-8'
    sel = Selector(resp)
    all_urls = sel.xpath("//section[@id='block-system-main']/div/div[contains(@class, 'row')]//a/@href").extract()
    article_urls = list(set(all_urls))
    if not article_urls:
        raise ValueError('article_urls获取失败！')
    news_urls = []
    for x in article_urls:
        if 'article' not in x:
            continue
        news_url = 'https://aawsat.com' + x
        news_urls.append(news_url)
    return news_urls

if __name__ == '__main__':
    # exit("已爬完！")
    requests.adapters.DEFAULT_RETRIES = 10  # 增加重连次数
    requests.packages.urllib3.disable_warnings()
    categories = [('last-page', 435),
                  ('culture', 180),
                  ('sport', 15),
                  ('economy', 18),
                  ('iran', 8),
                  ('world', 28),
                  ('arab-world', 53),
                  ('gulf', 7),
                  ('first', 7)]
    for cid, category in enumerate(categories):
        base_url = 'https://aawsat.com/home/international/section/' + category[0]
        if cid == 0 :
            start = 228
        else:
            start = 1
        for i in range(start, category[1]+1):
            url = base_url + "?page=" + str(i)
            prefix = str(cid) + '_' + str(i)
            news_urls = get_urls(url)
            for news_url in news_urls:
                get_news(news_url, prefix)
                time.sleep(1)
            time.sleep(1)