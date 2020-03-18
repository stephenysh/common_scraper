import requests
from scrapy import Selector
from fake_useragent import UserAgent
import time

ua = UserAgent()# 随机user-agent
headers = {
    "Host": 'alwatan.com',
    "User-Agent": ua.chrome
    }

def get_news_info(news_info_url, prefix):
    s = requests.Session()
    s.keep_alive = False  # 关闭多余连接
    repeat = 10
    while repeat:
        try:
            resp = s.get(news_info_url, headers=headers, verify=False, timeout=20)
            break
        except:
            print('trying:', repeat)
            repeat -= 1
            time.sleep(3)
    if repeat == 0:
        return
    resp.encoding = 'UTF-8'
    sel = Selector(resp)
    title = sel.xpath("//h1[contains(@class, 'post-title')]/text()").extract_first()
    contents = sel.xpath('//div[@class="entry"]/p//text()').extract()
    content = "\n".join(contents) if contents else ""
    target_file = 'alwatan/' + prefix + '.txt'
    print(news_info_url)
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
    target_file = 'alwatan/' + 'count_' + now_day + '.txt'
    with open(target_file, 'a', encoding='utf-8') as t:
        if content:
            t.write(news_info_url)
            t.write('\n')


def get_news_url(news_page_url, prefix):
    s = requests.Session()
    s.keep_alive = False  # 关闭多余连接
    repeat = 10
    while repeat:
        try:
            resp = s.get(news_page_url, headers=headers, verify=False, timeout=20)
            break
        except:
            print('trying:', repeat)
            repeat -= 1
            time.sleep(3)
    if repeat == 0:
        return
    resp.encoding = 'UTF-8'
    sel = Selector(resp)
    news_info_urls = sel.xpath("//article[contains(@class, 'item-list')]/h2/a/@href").extract()
    for news_info_url in news_info_urls:
        try:
            get_news_info(news_info_url, prefix)
        except Exception as e:
            print(e)
            continue


def get_clases(url, cid):
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
    resp.encoding = 'UTF-8'
    sel = Selector(resp)
    page = sel.xpath('//div[@class="pagination"]/span[1]/text()').extract_first().split(" ")[-1].replace(",","")
    if cid < 1:
        return
    if cid == 1:
        start = 220
    else:
        start = 1
    for i in range(start,int(page)+1):
        try:
            news_page_url = url + "/page/" + str(i)
            prefix = str(cid) + '_' + str(i)
            get_news_url(news_page_url, prefix)
        except:
            continue


if __name__ == '__main__':
    requests.adapters.DEFAULT_RETRIES = 10  # 增加重连次数
    requests.packages.urllib3.disable_warnings()
    urls = ['http://alwatan.com/section/front','http://alwatan.com/section/local','http://alwatan.com/section/politic','http://alwatan.com/section/economy','http://alwatan.com/section/sports','http://alwatan.com/section/opinion','http://alwatan.com/section/calture','http://alwatan.com/section/deen','http://alwatan.com/section/caricature%e2%80%8e','http://alwatan.com/section/ashreea','http://alwatan.com/section/qadaaia','http://alwatan.com/section/monaw3at','http://alwatan.com/section/technology','http://alwatan.com/archive','http://alwatan.com/archive','http://epaper.alwatan.com','http://www.alwatan.com/archieve.html','http://alwatan.com/links','http://alwatan.com/currency-rates','http://alwatan.com/oil','http://alwatan.com/climate','http://alwatan.com/prayer-times',]
    for cid, url in enumerate(urls):
        get_clases(url, cid)