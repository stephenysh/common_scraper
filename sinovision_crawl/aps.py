import time
import requests
from scrapy import Selector
from fake_useragent import UserAgent


ua = UserAgent()# 随机user-agent
headers = {
    "Host": 'www.aps.dz',
    "User-Agent": ua.chrome
    }

def get_news_info(news_url, prefix):
    s = requests.Session()
    s.keep_alive = False  # 关闭多余连接
    resp = s.get(news_url, headers=headers, verify=False, timeout=20)
    resp.encoding = 'UTF-8'
    sel = Selector(resp)
    title = sel.xpath('//*[@id="k2Container"]/div[1]/h2/text()').extract_first()
    contents = sel.xpath('//*[@id="k2Container"]/div[3]//text()').extract()
    content = "\n".join(contents) if contents else ""
    target_file = 'aps/' + prefix + '.txt'
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
    target_file = 'aps/' + 'count_' + now_day + '.txt'
    with open(target_file, 'a', encoding='utf-8') as t:
        if content:
            t.write(news_url)
            t.write('\n')

def get_news_url(news_page_url, prefix):
    s = requests.Session()
    s.keep_alive = False  # 关闭多余连接
    resp = s.get(news_page_url, headers=headers, verify=False, timeout=20)
    resp.encoding = 'UTF-8'
    sel = Selector(resp)
    news_urls = sel.xpath('//*[@id="itemListLeading"]/div/div/div[2]/h3/a/@href').extract()# 每个新闻的详细链接
    for news_url in news_urls:
        try:
            news_url = 'http://www.aps.dz' + news_url
            get_news_info(news_url, prefix)
        except Exception as e:
            print(e)
            continue


def get_classes(url, cid):
    s = requests.Session()
    s.keep_alive = False  # 关闭多余连接
    resp = s.get(url, headers=headers, verify=False, timeout=20)
    resp.encoding = 'UTF-8'
    sel = Selector(resp)
    page = sel.xpath('//*[@id="k2Container"]/div[3]/text()').extract_first().split(" ")[-1]
    if cid < 7:
        return
    if cid == 7:
        start = 211
    else:
        start = 1
    for i in range(start,int(page)+1):
        try:
            # 每个分类下的每一页的链接
            news_page_url = url + "?start=" + str((i-1)*10)
            prefix = str(cid) + '_' + str((i-1)*10)
            get_news_url(news_page_url, prefix)
        except:
            continue


if __name__ == '__main__':
    exit("已爬完！")
    requests.adapters.DEFAULT_RETRIES = 10  # 增加重连次数
    requests.packages.urllib3.disable_warnings()
    # urls 是http://www.aps.dz的每个分类的链接
    urls = ['http://www.aps.dz/ar/algerie','http://www.aps.dz/ar/economie','http://www.aps.dz/ar/monde','http://www.aps.dz/ar/sport','http://www.aps.dz/ar/societe','http://www.aps.dz/ar/culture','http://www.aps.dz/ar/regions','http://www.aps.dz/ar/sante-science-technologie',]
    for cid, url in enumerate(urls):
        get_classes(url, cid)