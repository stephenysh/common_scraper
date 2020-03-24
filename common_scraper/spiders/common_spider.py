from datetime import datetime
from urllib.parse import urlparse

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from common_scraper.items import CommonScraperItem
from common_scraper.util.cfg_util import url_prefix, start_url
from common_scraper.util.path_util import job_path
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
        'JOBDIR': str(job_path / name),
    }


    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        # random_url = redis_cli.randomkey()
        # if random_url is None:
        self.start_urls = [start_url]
        self.logger.info(f"use default title ./")
        # else:
        #     self.start_urls = [random_url]
        #     self.logger.info(f"use random url from redis")

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
        self.logger.info('Found one page! %s', url_keep)

        item = CommonScraperItem()
        item['url'] = url_keep
        item['date'] = datetime.utcnow()
        item['response'] = response.body.decode('utf-8', errors='ignore')

        redis_cli.set(url_keep, 'True')


        return item