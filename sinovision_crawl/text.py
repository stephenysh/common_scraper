import requests
from scrapy import Selector

headers = {
    # "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    # # "accept-encoding": 'gzip, deflate, br',
    # "accept-language": 'zh-CN,zh;q=0.9',
    # "cookie": '__cfduid=d84234e0f53ddd1c312c4d8e527d0a3641578905364; cf_clearance=c8c9b7d946e88032fa82dcbf898ba8995cb99c83-1578905376-0-250; _ga=GA1.2.1922199169.1578905377; _gid=GA1.2.1652765227.1578905378; ALs=51e515dc02a992966376e294f6cf2bc5',
    # "referer": 'https://www.addustour.com/categories/4-%D8%A7%D9%82%D8%AA%D8%B5%D8%A7%D8%AF',
    # "sec-fetch-mode": 'navigate',
    # "sec-fetch-site": 'same-origin',
    # "sec-fetch-user": '?1',
    # "upgrade-insecure-requests": '1',
    # "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
    "Accept": 'text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8',
    "Accept-Encoding": 'gzip, deflate, br',
    "Accept-Language": 'zh-Hans-CN, zh-Hans; q=0.5',
    "Cache-Control": 'max-age=0',
    "Cookie": '__cfduid=d84234e0f53ddd1c312c4d8e527d0a3641578905364; cf_clearance=c8c9b7d946e88032fa82dcbf898ba8995cb99c83-1578905376-0-250; _ga=GA1.2.1922199169.1578905377; _gid=GA1.2.1652765227.1578905378; ALs=51e515dc02a992966376e294f6cf2bc5',
    "Host": 'www.addustour.com',
    "Upgrade-Insecure-Requests": '1',
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363'
    }
resp = requests.get("https://www.addustour.com/categories/1-%D9%85%D8%AD%D9%84%D9%8A%D8%A7%D8%AA/page23",headers=headers)
# resp.encoding="UTF-8"
sel = Selector(resp)
print(resp.encoding)
# print(sel.xpath('//*[@id="al-right"]/div[2]/ul/li/a/@href').extract())