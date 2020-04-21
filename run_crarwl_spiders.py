import argparse

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from common_scraper.spiders.crawl_spiders import CommonSpider
from common_scraper.util.path_util import result_path


# can not run in multi process, so need manually start more multiple spiders

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    settings = get_project_settings()
    json_file = str(result_path / f'crawl_{CommonSpider.domain}.json')
    settings.attributes['FEED_URI'].set(json_file, 0)

    crawler = CrawlerProcess(settings)
    crawler.crawl(CommonSpider)
    crawler.start()




