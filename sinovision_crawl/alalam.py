import time
import requests
from scrapy import Selector
from fake_useragent import UserAgent

ua = UserAgent()# 随机user-agent
headers = {
    "Host": 'alalam.ma',
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
    title = sel.xpath('//div[@class="post-inner"]/h1/span/text()').extract_first()
    contents = sel.xpath('//div[@class="post-inner"]/div[@class="entry"]//text()').extract()
    content = "\n".join(contents) if contents else ""
    target_file = 'alalam/' + prefix + '.txt'
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
    target_file = 'alalam/' + 'count_' + now_day + '.txt'
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
    news_info_urls = sel.xpath('//div[@class="post-listing archive-box"]/article/h2/a/@href').extract()
    for news_info_url in news_info_urls:
        try:
            get_news_info(news_info_url, prefix)
            time.sleep(1)
        except Exception as e:
            print(e)
            continue


def get_page(news_url, cid):
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
    page = sel.xpath('//*[@id="main-content"]/div[1]/div[4]/span[1]/text()').extract_first().split(" ")[-1]
    if cid < 6:
        return
    if cid == 6:
        start = 130
    else:
        start = 1
    for i in range(start,int(page)+1):
        try:
            news_page_url = news_url + "/page/" + str(i) +"/"
            prefix = str(cid) + '_' + str(i)
            get_news_url(news_page_url, prefix)
        except:
            continue


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
    info_urls = sel.xpath('//div[@class="main-menu"]/ul/li[last()]/div/ul/li/a/@href|//div[@class="main-menu"]/ul/li[3]/div/ul/li/a/@href').extract()
    for cid, info_url in enumerate(info_urls):
        try:
            get_page(info_url, cid)
            time.sleep(1)
        except:
            continue


if __name__ == '__main__':
     exit("已爬完！")
    requests.adapters.DEFAULT_RETRIES = 10  # 增加重连次数
    requests.packages.urllib3.disable_warnings()
    url = "http://alalam.ma/"
    get_urls(url)
    time.sleep(1)