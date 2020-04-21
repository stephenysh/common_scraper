from urllib.parse import urlparse
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
    name = 'bbc_spider'
    start_urls = ['https://www.bbc.com/']
    redis_cli = getRedisClient(db=10)

    def parse(self, response):

        url_parsed = urlparse(response.url)

        path_parts = [p for p in url_parsed.path.split('/') if p != '']

        if url_parsed.netloc == 'www.bbc.com' and len(path_parts) > 1 and path_parts[0] in ["news", "sport", "worklife",
                                                                                            "travel", "culture"]:
            yield {
                'url': response.url,
                'response': response.body.decode('utf-8', errors='ignore')
            }
            self.redis_cli.set(response.url, 1)
            self.logger.info(f"found page: {response.url}")

        else:
            self.redis_cli.set(response.url, 0)

        for next_page in response.css(f"a[href^='https://www.bbc.com']"):
            if self.redis_cli.get(next_page.attrib['href']) is not None:
                continue
            yield response.follow(next_page, self.parse)

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
