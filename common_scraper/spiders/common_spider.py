from datetime import datetime
from urllib.parse import urlparse

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from common_scraper.items import CommonScraperItem
from common_scraper.util.cfg_util import url_prefix, start_url
from common_scraper.util.redis_util import redis_cli
from common_scraper.util.url_util import extract_valid_url

'''
1. use redis to share data with multi spider instance
2. just crawl the page and process data later
'''

class CommonSpider(CrawlSpider):
    domain = urlparse(url_prefix).netloc

    name = domain

    allowed_domains = [domain]

    rules = (
        Rule(LinkExtractor(allow=url_prefix), callback='parse_item', follow=True),
    )

    custom_settings = {
        'FEED_FORMAT': 'jsonlines',
        'FEED_EXPORT_ENCODING': 'utf-8',
        # 'JOBDIR': str(job_path / name),
        # 'DEPTH_LIMIT': 2
    }


    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        self.start_urls = [start_url]
        self.logger.info(f"use default title ./")

        self.logger.info(f'start crawler title url {self.start_urls}')


    def __del__(self):
        self.logger.info(f'crawler shutdown')


    def parse_item(self, response):

        # this is for those valid url to duplicate, like with postfix ?page=1, will only keep the valid part of url
        url_keep = extract_valid_url(response.url)

        # Skip page with error response
        if not response.status == 200:
            self.logger.warning(f'Skip page with error response {url_keep}')
            return None

        # Skip page with error response
        if redis_cli.get(response.url) is not None:
            self.logger.warning(f'Skip page with duplicate redis record {url_keep}')
            return None

        ################# real process
        redis_cli.set(url_keep, 'True')

        # if not want_url(url_keep):
        #     return None

        # l = response.xpath(
        #     "//nav[@class='breadcrumb']//a[@href='/news/newssection/117/1/أخبار-السيارات'][@title='أخبار السيارات']")
        # if len(l) == 0:
        #     return None

        # https://news.un.org/ar/story/2020/04/1052982
        # l = response.xpath(
        #     "//div[@class='content']//a[@href='/ar/news/topic/women']")
        # if len(l) == 0:
        #     return None
        # https: // edition.cnn.com / 2017 / 11 / 10 / health / screen - decisions - go - ask - your - dad / index.html

        url_parsed = urlparse(url_keep)

        # cnn
        # if not re.match("^(/\d+){3}(/[^/]+)+$", url_parsed.path):
        #   return None

        # bbc
        path_parts = [p for p in url_parsed.path.split('/') if p != '']

        if len(path_parts) != 1 and path_parts[0] in ["news", "sport", "worklife", "travel", "culture"]:
            self.logger.info('Found one page! %s', url_keep)

            item = CommonScraperItem()
            item['url'] = url_keep
            item['date'] = datetime.utcnow()
            item['response'] = response.body.decode('utf-8', errors='ignore')

            return item
