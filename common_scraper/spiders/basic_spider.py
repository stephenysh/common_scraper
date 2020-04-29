from urllib.parse import urlparse, urljoin
import re
import scrapy

from util.redis_util import getRedisClient


class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://blog.scrapinghub.com']

    def parse(self, response):
        for title in response.css('.post-header>h2'):
            yield {'title': title.css('a ::text').get()}

        for next_page in response.css('a.next-posts-link'):
            yield response.follow(next_page, self.parse)


class UnSpider(scrapy.Spider):
    name = 'un_spider'
    start_urls = ['https://news.un.org/ar/news/topic/women']

    def parse(self, response):
        for title in response.css('h1.story-title'):
            yield {
                'title': title.css('a ::text').get(),
                'url': title.css('a').attrib['href'],
                'page': response.css('ul.pagination li.active span::text').get()
            }

        for next_page in response.css('li.next a'):
            yield response.follow(next_page, self.parse)


class BBCSpider(scrapy.Spider):
    name = 'bbc_spider_food'
    base_url = 'https://www.bbc.co.uk/food/articles/'
    start_urls = ['https://www.bbc.co.uk/food']
    redis_cli = getRedisClient(db=11)

    def parse(self, response):

        url_parsed = urlparse(response.url)

        if url_parsed.netloc == 'www.bbc.co.uk' and response.url.startswith(self.base_url) and self.redis_cli.get(response.url) is None:
            yield {
                'url': response.url,
                'response': response.body.decode('utf-8', errors='ignore')
            }
            self.redis_cli.set(response.url, 1)
            self.logger.info(f"found page: {response.url}")

        else:
            self.redis_cli.set(response.url, 0)

        for idx, next_page in enumerate(response.css(f"a[href], link[href]")):
            absolute_url = urljoin(self.base_url, next_page.attrib['href'])

            if not absolute_url.startswith(self.base_url):
                continue
            if self.redis_cli.get(absolute_url) is not None:
                continue

            yield response.follow(absolute_url, self.parse)

class CNNSpider(scrapy.Spider):
    name = 'cnn_spider'
    start_urls = ['https://edition.cnn.com/2020/04/20/investing/premarket-stocks-trading/index.html']
    redis_cli = getRedisClient(db=10)

    def parse(self, response):

        url_parsed = urlparse(response.url)

        if re.match("^(/\d+){3}(/[^/]+)+$", url_parsed.path):


            yield {
                'url': response.url,
                'response': response.body.decode('utf-8', errors='ignore')
            }
            self.redis_cli.set(response.url, 1)
            self.logger.info(f"found page: {response.url}")

        else:
            self.redis_cli.set(response.url, 0)

        for next_page in response.css(f"a[href^='/']"):
            if self.redis_cli.get(next_page.attrib['href']) is not None:
                continue
            yield response.follow(next_page, self.parse)


class GuardianSpider(scrapy.Spider):
    name = 'guardian_spider_travel'
    base_url = 'https://www.theguardian.com/travel'
    start_urls = ['https://www.theguardian.com/uk/travel']
    redis_cli = getRedisClient(db=11)

    def parse(self, response):

        url_parsed = urlparse(response.url)

        path_parts = [p for p in url_parsed.path.split('/') if p != '']

        if url_parsed.netloc == 'www.theguardian.com' and len(path_parts) > 1 and path_parts[0] in ["travel"] and self.redis_cli.get(response.url) is None:
            yield {
                'url': response.url,
                'response': response.body.decode('utf-8', errors='ignore')
            }
            self.redis_cli.set(response.url, 1)
            self.logger.info(f"found page: {response.url}")

        else:
            self.redis_cli.set(response.url, 0)

        for idx, next_page in enumerate(response.css(f"a[href], link[href]")):
            absolute_url = urljoin(self.base_url, next_page.attrib['href'])
            absolute_url_parts = [p for p in urlparse(absolute_url).path.split('/') if p != '']

            if not absolute_url.startswith(self.base_url):
                continue
            if len(absolute_url_parts) <= 1 or absolute_url_parts[0] not in ["travel"]:
                continue
            if '.' in absolute_url_parts[-1]:
                continue
            if self.redis_cli.get(absolute_url) is not None:
                continue

            yield response.follow(absolute_url, self.parse)

class ArabBusinessSpider(scrapy.Spider):
    name = 'arab_business_spider_education'
    base_url = 'https://www.arabianbusiness.com/education'
    start_urls = ['https://www.arabianbusiness.com/education/433068-abu-dhabi-al-ain-to-get-new-kindergartens-in-45m-investment']
    redis_cli = getRedisClient(db=11)

    def parse(self, response):

        url_parsed = urlparse(response.url)

        path_parts = [p for p in url_parsed.path.split('/') if p != '']

        if url_parsed.netloc == 'www.arabianbusiness.com' and len(path_parts) > 1 and path_parts[0] in ["education"] and self.redis_cli.get(response.url) is None:
            yield {
                'url': response.url,
                'response': response.body.decode('utf-8', errors='ignore')
            }
            self.redis_cli.set(response.url, 1)
            self.logger.info(f"found page: {response.url}")

        else:
            self.redis_cli.set(response.url, 0)

        for idx, next_page in enumerate(response.css(f"a[href], link[href]")):
            absolute_url = urljoin(self.base_url, next_page.attrib['href'])
            absolute_url_parts = [p for p in urlparse(absolute_url).path.split('/') if p != '']

            if not absolute_url.startswith(self.base_url):
                continue
            if len(absolute_url_parts) <= 1 or absolute_url_parts[0] not in ["education"]:
                continue
            if '.' in absolute_url_parts[-1]:
                continue
            if self.redis_cli.get(absolute_url) is not None:
                continue

            yield response.follow(absolute_url, self.parse)