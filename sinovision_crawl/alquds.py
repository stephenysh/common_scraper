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
    title = sel.xpath('//*[@id="article"]/div/h1/text()').extract_first()
    contents = sel.xpath('//*[@id="paragraphs"]/p/text()').extract()
    content = "\n".join(contents) if contents else ""
    target_file = 'alquds/' + prefix + '.txt'
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
    target_file = 'alquds/' + 'count_' + now_day + '.txt'
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
    first_article_url = sel.xpath("//div[@id='search_container']/div/div/article/div/a/@href").extract_first()
    article_urls = sel.xpath("//div[@id='channel-listing']/article/div/a/@href").extract()
    article_urls.append(first_article_url)
    if not article_urls:
        raise ValueError('article_urls获取失败！')
    news_urls = []
    for x in article_urls:
        news_url = 'http://www.alquds.com' + x.replace('/lang/ar', '')
        news_urls.append(news_url)
    return news_urls

if __name__ == '__main__':
    exit("已爬完！")
    requests.adapters.DEFAULT_RETRIES = 10  # 增加重连次数
    requests.packages.urllib3.disable_warnings()
    categories = [('miscellaneous', 334),
                  ('computer_and_mobile', 276),
                  ('medicine_and_health', 285),
                  ('business', 334),
                  ('sports', 334),
                  ('opinions', 324),
                  ('palestinian_territories', 334),
                  ('reports_and_analysis', 34)]
    for cid, category in enumerate(categories):
        base_url = 'http://www.alquds.com/channels/' + category[0]
        if cid == 0:
            start = 161
        else:
            start = 1
        for i in range(start, category[1]+1):
            if i*30 > 10000:
                page_name = str(i * 30 - 29) + '-' + str(10000)
            else:
                page_name = str(i * 30 - 29) + '-' + str(i * 30)
            url = base_url + "/" + page_name
            prefix = str(cid) + '_' + page_name
            news_urls = get_urls(url)
            print(page_name)
            for news_url in news_urls:
                get_news(news_url, prefix)
                time.sleep(1)
            time.sleep(1)