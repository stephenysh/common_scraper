import time
import requests
from scrapy import Selector
from fake_useragent import UserAgent

ua = UserAgent()# 随机user-agent
headers = {
    # "referer": 'https://www.raya.com/news/locals',
    "User-Agent": ua.chrome
    }

def get_news_info(news_url, prefix):
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
    title = sel.xpath('//*[@id="the-post"]/div[2]/h1/span/text()').extract_first()
    contents = sel.xpath('//div[@class="entry"]//text()').extract()
    content = "\n".join(contents) if contents else ""
    target_file = 'nbprs/' + prefix + '.txt'
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
    target_file = 'nbprs/' + 'count_' + now_day + '.txt'
    with open(target_file, 'a', encoding='utf-8') as t:
        if content:
            t.write(news_url)
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
    news_urls = sel.xpath('//div[@class="post-listing archive-box"]/article/h2/a/@href').extract()
    for news_url in news_urls:
        get_news_info(news_url, prefix)

def get_news_page(url, cid):
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
    page = sel.xpath('//div[@class="pagination"]/span[1]/text()').extract_first().split(" ")[-1]
    if cid < 42:
        return
    if cid == 42:
        start = 39
    else:
        start = 1
    for i in range(start,int(page)+1):
        news_page_url = url + 'page/' + str(i) + '/'
        prefix = str(cid) + '_' + str(i)
        get_news_url(news_page_url, prefix)


if __name__ == '__main__':
    exit("已爬完！")
    requests.adapters.DEFAULT_RETRIES = 10  # 增加重连次数
    requests.packages.urllib3.disable_warnings()
    urls = [
'http://nbprs.ps/category/%d8%aa%d8%b5%d8%b1%d9%8a%d8%ad%d8%a7%d8%aa-%d8%aa%d9%8a%d8%b3%d9%8a%d8%b1-%d8%ae%d8%a7%d9%84%d8%af/',
'http://nbprs.ps/category/%d9%85%d9%82%d8%a7%d9%84%d8%a7%d8%aa-%d9%88%d8%aa%d9%82%d8%a7%d8%b1%d9%8a%d8%b1/',
'http://nbprs.ps/category/%d9%85%d9%82%d8%a7%d9%84%d8%a7%d8%aa-%d9%88%d8%aa%d9%82%d8%a7%d8%b1%d9%8a%d8%b1/%d8%aa%d9%82%d8%b1%d9%8a%d8%b1-%d8%a7%d9%84%d8%a7%d8%b3%d8%aa%d9%8a%d8%b7%d8%a7%d9%86/',
'http://nbprs.ps/category/%d9%85%d9%82%d8%a7%d9%84%d8%a7%d8%aa-%d9%88%d8%aa%d9%82%d8%a7%d8%b1%d9%8a%d8%b1/%d9%85%d9%82%d8%a7%d9%84%d8%a7%d8%aa-%d9%85%d9%86%d9%88%d8%b9%d8%a9/',
'http://nbprs.ps/category/%d9%85%d9%82%d8%a7%d9%84%d8%a7%d8%aa-%d9%88%d8%aa%d9%82%d8%a7%d8%b1%d9%8a%d8%b1/%d9%85%d9%82%d8%a7%d9%84%d8%a7%d8%aa-%d8%a7%d9%82%d8%aa%d8%b5%d8%a7%d8%af%d9%8a%d8%a9/',
'http://nbprs.ps/category/%d8%b4%d8%a4%d9%88%d9%86-%d8%b9%d8%a7%d9%84%d9%85%d9%8a%d8%a9/',
'http://nbprs.ps/category/%d8%b4%d8%a4%d9%88%d9%86-%d8%a7%d8%b3%d8%b1%d8%a7%d8%a6%d9%8a%d9%84%d9%8a%d8%a9/',
'http://nbprs.ps/category/%d8%b4%d8%a4%d9%88%d9%86-%d8%b9%d8%b1%d8%a8%d9%8a%d8%a9/',
'http://nbprs.ps/category/%d8%ac%d8%b1%d8%a7%d8%a6%d9%85-%d9%88%d8%a7%d9%86%d8%aa%d9%87%d8%a7%d9%83%d8%a7%d8%aa/',
'http://nbprs.ps/category/%d8%b5%d8%ad%d9%81/',
'http://nbprs.ps/category/%d8%b5%d8%ad%d9%81/%d8%b5%d8%ad%d9%81-%d9%81%d9%84%d8%b3%d8%b7%d9%8a%d9%86%d8%a9/',
'http://nbprs.ps/category/%d8%b5%d8%ad%d9%81/%d8%b5%d8%ad%d9%81-%d8%b9%d8%b1%d8%a8%d9%8a%d8%a9/',
'http://nbprs.ps/category/%d8%b5%d8%ad%d9%81/%d8%b5%d8%ad%d9%81-%d8%b9%d8%a7%d9%84%d9%85%d9%8a%d8%a9/',
'http://nbprs.ps/category/%d8%b5%d8%ad%d9%81/%d8%b5%d8%ad%d9%81-%d8%b9%d8%a8%d8%b1%d9%8a%d8%a9/',
'http://nbprs.ps/category/%d9%88%d8%ab%d8%a7%d8%a6%d9%82/',
'http://nbprs.ps/category/%d9%85%d9%83%d8%aa%d8%a8%d8%a9-%d8%a7%d9%84%d9%81%d9%8a%d8%af%d9%8a%d9%88/',
'http://nbprs.ps/%D8%B9%D9%86-%D8%A7%D9%84%D9%85%D9%83%D8%AA%D8%A8/',
'http://nbprs.ps/category/%d9%85%d9%84%d9%81-%d8%a7%d9%84%d8%a7%d8%b3%d8%aa%d9%8a%d8%b7%d8%a7%d9%86/',
'http://nbprs.ps/category/%d9%85%d9%84%d9%81-%d8%a7%d9%84%d9%82%d8%af%d8%b3/',
'http://nbprs.ps/category/%d9%85%d9%84%d9%81-%d8%a7%d9%84%d8%a7%d8%b3%d8%b1%d9%89/',
'http://nbprs.ps/category/%d9%85%d9%84%d9%81-%d8%a7%d9%84%d9%85%d9%82%d8%a7%d8%b7%d8%b9%d8%a9/',
'http://nbprs.ps/category/%d9%85%d9%84%d9%81-%d8%a7%d9%84%d9%85%d9%8a%d8%a7%d9%87/',
'http://nbprs.ps/category/%d8%aa%d8%b5%d8%b1%d9%8a%d8%ad%d8%a7%d8%aa-%d8%aa%d9%8a%d8%b3%d9%8a%d8%b1-%d8%ae%d8%a7%d9%84%d8%af/',
'http://nbprs.ps/category/%d9%85%d9%82%d8%a7%d9%84%d8%a7%d8%aa-%d9%88%d8%aa%d9%82%d8%a7%d8%b1%d9%8a%d8%b1/',
'http://nbprs.ps/category/%d9%85%d9%82%d8%a7%d9%84%d8%a7%d8%aa-%d9%88%d8%aa%d9%82%d8%a7%d8%b1%d9%8a%d8%b1/%d8%aa%d9%82%d8%b1%d9%8a%d8%b1-%d8%a7%d9%84%d8%a7%d8%b3%d8%aa%d9%8a%d8%b7%d8%a7%d9%86/',
'http://nbprs.ps/category/%d9%85%d9%82%d8%a7%d9%84%d8%a7%d8%aa-%d9%88%d8%aa%d9%82%d8%a7%d8%b1%d9%8a%d8%b1/%d9%85%d9%82%d8%a7%d9%84%d8%a7%d8%aa-%d9%85%d9%86%d9%88%d8%b9%d8%a9/',
'http://nbprs.ps/category/%d9%85%d9%82%d8%a7%d9%84%d8%a7%d8%aa-%d9%88%d8%aa%d9%82%d8%a7%d8%b1%d9%8a%d8%b1/%d9%85%d9%82%d8%a7%d9%84%d8%a7%d8%aa-%d8%a7%d9%82%d8%aa%d8%b5%d8%a7%d8%af%d9%8a%d8%a9/',
'http://nbprs.ps/category/%d8%b4%d8%a4%d9%88%d9%86-%d8%b9%d8%a7%d9%84%d9%85%d9%8a%d8%a9/',
'http://nbprs.ps/category/%d8%b4%d8%a4%d9%88%d9%86-%d8%a7%d8%b3%d8%b1%d8%a7%d8%a6%d9%8a%d9%84%d9%8a%d8%a9/',
'http://nbprs.ps/category/%d8%b4%d8%a4%d9%88%d9%86-%d8%b9%d8%b1%d8%a8%d9%8a%d8%a9/',
'http://nbprs.ps/category/%d8%ac%d8%b1%d8%a7%d8%a6%d9%85-%d9%88%d8%a7%d9%86%d8%aa%d9%87%d8%a7%d9%83%d8%a7%d8%aa/',
'http://nbprs.ps/category/%d8%b5%d8%ad%d9%81/',
'http://nbprs.ps/category/%d8%b5%d8%ad%d9%81/%d8%b5%d8%ad%d9%81-%d9%81%d9%84%d8%b3%d8%b7%d9%8a%d9%86%d8%a9/',
'http://nbprs.ps/category/%d8%b5%d8%ad%d9%81/%d8%b5%d8%ad%d9%81-%d8%b9%d8%b1%d8%a8%d9%8a%d8%a9/',
'http://nbprs.ps/category/%d8%b5%d8%ad%d9%81/%d8%b5%d8%ad%d9%81-%d8%b9%d8%a7%d9%84%d9%85%d9%8a%d8%a9/',
'http://nbprs.ps/category/%d8%b5%d8%ad%d9%81/%d8%b5%d8%ad%d9%81-%d8%b9%d8%a8%d8%b1%d9%8a%d8%a9/',
'http://nbprs.ps/category/%d9%88%d8%ab%d8%a7%d8%a6%d9%82/',
'http://nbprs.ps/category/%d9%85%d9%83%d8%aa%d8%a8%d8%a9-%d8%a7%d9%84%d9%81%d9%8a%d8%af%d9%8a%d9%88/',
'http://nbprs.ps/%D8%B9%D9%86-%D8%A7%D9%84%D9%85%D9%83%D8%AA%D8%A8/',
'http://nbprs.ps/category/%d9%85%d9%84%d9%81-%d8%a7%d9%84%d8%a7%d8%b3%d8%aa%d9%8a%d8%b7%d8%a7%d9%86/',
'http://nbprs.ps/category/%d9%85%d9%84%d9%81-%d8%a7%d9%84%d9%82%d8%af%d8%b3/',
'http://nbprs.ps/category/%d9%85%d9%84%d9%81-%d8%a7%d9%84%d8%a7%d8%b3%d8%b1%d9%89/',
'http://nbprs.ps/category/%d9%85%d9%84%d9%81-%d8%a7%d9%84%d9%85%d9%82%d8%a7%d8%b7%d8%b9%d8%a9/',
'http://nbprs.ps/category/%d9%85%d9%84%d9%81-%d8%a7%d9%84%d9%85%d9%8a%d8%a7%d9%87/'
    ]
    for cid, url in enumerate(urls):
        try:
            get_news_page(url, cid)
        except:
            continue
