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
    title = sel.xpath("//div[contains(@class,'article_intro')]/h1/text()").extract_first()
    contents = sel.xpath('//*[@id="readspeaker_maincontent"]//p/text()').extract()
    content = "\n".join(contents) if contents else ""
    target_file = 'annahar/' + prefix + '.txt'
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
    target_file = 'annahar/' + 'count_' + now_day + '.txt'
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
    article_urls = sel.xpath("//article[starts-with(@class,'article-')]//a/@href").extract()
    if not article_urls:
        raise ValueError('article_urls获取失败！')
    news_urls = []
    for x in article_urls:
        news_url = 'https://www.annahar.com' + x
        news_urls.append(news_url)
    return news_urls

if __name__ == '__main__':
    exit("已爬完！")
    requests.adapters.DEFAULT_RETRIES = 10  # 增加重连次数
    requests.packages.urllib3.disable_warnings()
    categories = [('3-%D8%B1%D9%8A%D8%A7%D8%B6%D8%A9', 300),
                  ('314-%D8%AB%D9%82%D8%A7%D9%81%D8%A9', 117),
                  ('2-%D8%A5%D9%82%D8%AA%D8%B5%D8%A7%D8%AF', 300),
                  ('533-%D9%84%D8%A7%D9%8A%D9%81-%D8%B3%D8%AA%D8%A7%D9%8A%D9%84', 300),
                  ('1-%D9%84%D8%A8%D9%86%D8%A7%D9%86', 300)]
    for cid, category in enumerate(categories):
        base_url = 'https://www.annahar.com/section'
        if cid < 2:
            continue
        if cid == 2:
            start = 131
        else:
            start = 1
        for i in range(start, category[1]+1):
            url = base_url + "/" + str(i) + '/' + category[0]
            prefix = str(cid) + '_' + str(i)
            news_urls = get_urls(url)
            for news_url in news_urls:
                get_news(news_url, prefix)
                time.sleep(1)
            time.sleep(1)