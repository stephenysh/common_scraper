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
    title = sel.xpath('//*[@class="title-wrap"]/h1/text()').extract_first()
    contents = sel.xpath('//*[@id="primary"]//p/text()').extract()
    content = "\n".join(contents) if contents else ""
    target_file = 'al-jazirahonline/' + prefix + '.txt'
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
    target_file = 'al-jazirahonline/' + 'count_' + now_day + '.txt'
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
    news_urls = sel.xpath('//*[@class="title-wrap"]/h3/a/@href').extract()
    resp.close()
    if not news_urls:
        raise ValueError('news_urls获取失败！')
    return news_urls

if __name__ == '__main__':
    exit("已爬完！")
    requests.adapters.DEFAULT_RETRIES = 10  # 增加重连次数
    requests.packages.urllib3.disable_warnings()
    categories = [('%D8%A7%D9%84%D9%88%D8%B3%D8%A7%D8%A6%D8%B7', 53),
                  ('%D8%A7%D9%84%D9%85%D8%AC%D8%AA%D9%85%D8%B9', 155),
                  ('%D8%A7%D9%84%D9%85%D8%B1%D8%A3%D8%A9', 22),
                  ('%D8%A7%D9%84%D9%85%D9%86%D9%88%D8%B9%D8%A7%D8%AA', 99),
                  ('sport', 99),
                  ('world', 159),
                  ('%D8%A7%D9%84%D9%85%D9%85%D9%84%D9%83%D8%A9', 159)]
    for cid, category in enumerate(categories):
        base_url = 'http://www.al-jazirahonline.com/category/' + category[0]
        if cid < 4:
            continue
        if cid == 4:
            start = 89
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