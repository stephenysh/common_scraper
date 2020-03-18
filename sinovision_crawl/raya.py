import requests
import time
from scrapy import Selector
from fake_useragent import UserAgent
ua = UserAgent()# 随机user-agent
headers = {
    "referer": 'https://www.raya.com/news/locals',
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
    title = sel.xpath("//*[@id='detailed_rightCont']/div[1]/div[@class='detailed2_rightRightHeader']/h2/text()").extract_first()
    contents = sel.xpath("//*[@id='detailed_rightCont']/div[1]/div[@class='detailed_rightRightText']//span/text()").extract()
    content = "\n".join(contents) if contents else ""
    target_file = 'raya/' + prefix + '.txt'
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
    target_file = 'raya/' + 'count_' + now_day + '.txt'
    with open(target_file, 'a', encoding='utf-8') as t:
        if content:
            t.write(news_url)
            t.write('\n')

def get_news_url(url, cid):
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
    news_urls = sel.xpath('//div[@class="summary_secondarticle"]/div/div[2]/a/@href|//div[@class="summary_secondarticle_headlines"]//tr/td/a/@href').extract()
    for i, news_url in enumerate(news_urls):
        if cid < 30:
            return
        if cid == 30 and i < 26:
            continue
        news_url = 'https://www.raya.com' + news_url
        prefix = str(cid) + '_' + str(i)
        get_news_info(news_url, prefix)

if __name__ == '__main__':
    exit("可能好像貌似也许爬完了......")
    requests.adapters.DEFAULT_RETRIES = 10  # 增加重连次数
    requests.packages.urllib3.disable_warnings()
    urls = ['https://www.raya.com/news/locals', 'https://www.raya.com/news/LocalInvestigations','https://www.raya.com/news/ArabicNews', 'https://www.raya.com/news/InternationalNews','https://www.raya.com/news/PoliticalInvestigations', 'https://www.raya.com/news/Dialogues','https://www.raya.com/news/Events', 'https://www.raya.com/news/Reports','https://www.raya.com/news/Issues', 'https://www.raya.com/news/Rebounds','https://www.raya.com/news/Studies', 'https://www.raya.com/news/DiplomaticBag','https://www.raya.com/news/RayaEconomic', 'https://www.raya.com/news/RayaSports','https://www.raya.com/news/Wedding', 'https://www.raya.com/news/Mortality','https://www.raya.com/writers/pages', 'https://www.raya.com/news/Forum','https://www.raya.com/news/FreePlatform', 'https://www.raya.com/news/IslamBanner','https://www.raya.com/news/Crime', 'https://www.raya.com/news/ConfusedSouls','https://www.raya.com/news/Translations', 'https://www.raya.com/news/RadioAndTV','https://www.raya.com/news/ProspectsAndArts', 'https://www.raya.com/news/cultureandcivility','https://www.raya.com/news/variouspages', 'https://www.raya.com/news/cinema','https://www.raya.com/portal/pages/a981ad00-5d87-4a92-9e43-4d34d4628b2c','https://www.raya.com/portal/pages/d86be441-af5e-4b1d-9bc8-b5e08728c3ca','https://www.raya.com/news/LatsetAndPanorama']
    for cid, url in enumerate(urls):
        get_news_url(url, cid)