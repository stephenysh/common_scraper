import time
import requests
from scrapy import Selector

headers = {
    "Accept": 'text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8',
    # "Accept-Encoding": 'gzip, deflate, br',
    "Accept-Language": 'zh-CN,zh;q=0.9',
    "Cache-Control": 'max-age=0',
    "Cookie": 'cf_clearance=ea2b3e04bded706ff7978fbd92b61bf163c91469-1579604232-0-250; __cfduid=d5da5233bff7d49a3203df0474113ca6e1579604232; ALs=dc5f533d31714acc3cd3672cc582d2c1; _ga=GA1.2.1517880621.1579604339; _gid=GA1.2.1272238848.1579604339',
    "Host": 'www.addustour.com',
    "Upgrade-Insecure-Requests": '1',
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
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
    title = sel.xpath('//*[@id="article_title"]/h2/text()').extract_first()
    contents = sel.xpath('//*[@id="article_text"]/p//text()').extract()
    content = "\n".join(contents) if contents else ""
    target_file = 'addustour/' + prefix + '.txt'
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
    target_file = 'addustour/' + 'count_' + now_day + '.txt'
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
    info_urls = sel.xpath('//*[@id="al-right"]/div[2]/ul/li/a/@href').extract()
    if not info_urls:
        raise ValueError("cookie 失效！")

    news_urls = []
    for info_url in info_urls:
        news_url = "https://www.addustour.com" + info_url.replace("../..","")
        news_urls.append(news_url)

    return news_urls

if __name__ == '__main__':
    requests.adapters.DEFAULT_RETRIES = 10  # 增加重连次数
    requests.packages.urllib3.disable_warnings()
    categories = [('1-%D9%85%D8%AD%D9%84%D9%8A%D8%A7%D8%AA', 17895),
                  ('2-%D9%85%D8%AD%D8%A7%D9%81%D8%B8%D8%A7%D8%AA', 3056),
                  ('4-%D8%A7%D9%82%D8%AA%D8%B5%D8%A7%D8%AF', 6062),
                  ('5-%D8%B9%D8%B1%D8%A8%D9%8A-%D9%88%D8%AF%D9%88%D9%84%D9%8A', 9024),
                  ('7-%D8%B1%D9%8A%D8%A7%D8%B6%D8%A9', 7476),
                  ('3-%D8%AB%D9%82%D8%A7%D9%81%D8%A9', 2719),
                  ('6-%D8%AF%D8%B1%D9%88%D8%A8', 4520),
                  ('32-%D8%B4%D8%A8%D8%A7%D8%A8', 9),
                  ('33-%D8%AC%D8%A7%D9%85%D8%B9%D8%A7%D8%AA', 58)]
    for cid, category in enumerate(categories):
        base_url = 'https://www.addustour.com/categories/' + category[0]
        if cid == 0:
            start = 4502
        else:
            start = 1
        for i in range(start, category[1]+1):
            url = base_url + "/page" + str(i)
            prefix = category[0].split('-')[0] + '_' + str(i)
            news_urls = get_urls(url)
            for news_url in news_urls:
                get_news(news_url, prefix)
                time.sleep(1)
            time.sleep(1)