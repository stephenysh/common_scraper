import re
import redis
import urllib.parse
from datetime import datetime
from urllib.parse import urlparse, urljoin, unquote

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from common_scraper.items import CommonScraperItem

from common_scraper.redis_util import redis_cli

from common_scraper.util import result_path
'''
1. use redis to share data with multi spider instance
2. just crawl the page and process data later
'''

'https://www.bbc.com/arabic/'
class CommonSpider(CrawlSpider):
    name = 'common_spider'

    url_prefix = f'https://www.bbc.com/arabic/'

    domain = urlparse(url_prefix).netloc

    allowed_domains = [domain]

    rules = (
        Rule(LinkExtractor(allow=url_prefix), callback='parse_item', follow=True),
    )

    custom_settings = {
        'FEED_FORMAT': 'jsonlines',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }


    def __init__(self, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)

        if 'title' in kwargs:
            self.start_urls = [urljoin(self.url_prefix, kwargs['title'])]
        else:
            random_url = redis_cli.randomkey()
            if random_url is None:
                raise RuntimeError('nothing in redis, should set start title.')
            self.start_urls = [random_url]

        self.logger.info(f'start crawler title url {self.start_urls}')


    def __del__(self):
        self.logger.info(f'crawler shutdown')


    def parse_item(self, response):

        url_unquoted = unquote(response.url)

        self.logger.info(f'get into page {url_unquoted}')

        # Skip page with error response
        if not response.status == 200:
            self.logger.warning(f'Skip page with error response {url_unquoted}')
            return None

        ################# real process
        self.logger.info('Found one page! %s', url_unquoted)

        item = CommonScraperItem()
        item['url'] = response.url
        item['date'] = datetime.utcnow()

        # item['response'] = response.body.decode('utf-8')

        redis_cli.set(response.url, 'True')


        return item