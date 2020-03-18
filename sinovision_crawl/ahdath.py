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
    title = sel.xpath('//*[@class="single-heading"]/span/text()').extract_first()
    contents = sel.xpath('//*[@class="single-content"]/p//text()').extract()
    content = "\n".join(contents[1:]) if contents else ""
    target_file = 'ahdath/' + prefix + '.txt'
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
    resp.close()
    now_day = time.strftime("%Y-%m-%d", time.localtime())
    target_file = 'ahdath/' + 'count_' + now_day + '.txt'
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
    news_urls = sel.xpath('//*[@class="articles-xad archive-infinite"]/li/a/@href').extract()
    resp.close()
    return news_urls

if __name__ == '__main__':
    exit("已爬完！")
    requests.adapters.DEFAULT_RETRIES = 10  # 增加重连次数
    requests.packages.urllib3.disable_warnings()
    categories = [('%D8%A3%D8%AD%D8%AF%D8%A7%D8%AB-%D8%B1%D9%8A%D8%A7%D8%B6%D9%8A%D8%A9', 1905),
                  ('%D8%A3%D8%AD%D8%AF%D8%A7%D8%AB-%D9%81%D9%86%D9%8A%D8%A9', 1077),
                  ('%D8%A3%D8%AD%D8%AF%D8%A7%D8%AB-%D8%A7%D9%82%D8%AA%D8%B5%D8%A7%D8%AF%D9%8A%D8%A9', 568),
                  ('%D8%A3%D8%AD%D8%AF%D8%A7%D8%AB-%D8%B3%D9%8A%D8%A7%D8%B3%D9%8A%D8%A9', 1045),
                  ('%D8%A3%D8%AD%D8%AF%D8%A7%D8%AB-%D9%85%D8%AD%D9%84%D9%8A%D8%A9', 2270)]
    for cid, category in enumerate(categories):
        base_url = 'http://ahdath.info/category/' + category[0]
        if cid < 4:
            continue
        if cid == 4:
            start = 502
        else:
            start = 1
        for i in range(start, category[1]+1):
            url = base_url + "/page/" + str(i)
            prefix = str(cid) + '_' + str(i)
            news_urls = get_urls(url)
            for news_url in news_urls:
                get_news(news_url, prefix)
                time.sleep(1)
            time.sleep(1)