from datetime import datetime
from urllib.parse import urlparse, urljoin, unquote

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from common_scraper.items import CommonScraperItem

from common_scraper.util.redis_util import redis_cli

from common_scraper.util.path_util import job_path

from common_scraper.util.cfg_util import url_prefix, url_name, start_url

'''
1. use redis to share data with multi spider instance
2. just crawl the page and process data later
'''

class CommonSpider(CrawlSpider):
    name = url_name

    domain = urlparse(url_prefix).netloc

    allowed_domains = [domain]

    rules = (
        Rule(LinkExtractor(allow=url_prefix), callback='parse_item', follow=True),
    )

    custom_settings = {
        'FEED_FORMAT': 'jsonlines',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'JOBDIR': str(job_path / url_name),
    }


    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        random_url = redis_cli.randomkey()
        if random_url is None:
            self.start_urls = [start_url]
            self.logger.info(f"use default title ./")
        else:
            self.start_urls = [random_url]
            self.logger.info(f"use random url from redis")

        self.logger.info(f'start crawler title url {self.start_urls}')


    def __del__(self):
        self.logger.info(f'crawler shutdown')


    def parse_item(self, response):

        url_unquoted = unquote(response.url)

        # Skip page with error response
        if not response.status == 200:
            self.logger.warning(f'Skip page with error response {url_unquoted}')
            return None

        # Skip page with error response
        if redis_cli.get(response.url) is not None:
            self.logger.warning(f'Skip page with duplicate redis record {url_unquoted}')
            return None

        ################# real process
        self.logger.info('Found one page! %s', url_unquoted)

        item = CommonScraperItem()
        item['url'] = response.url
        item['date'] = datetime.utcnow()
        item['response'] = response.body.decode('utf-8')

        redis_cli.set(response.url, 'True')


        return item