import argparse

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from common_scraper.spiders.common_spider import CommonSpider

from common_scraper.util.path_util import result_path

# can not run in multi process, so need manually start more multiple spiders

def start_spider(idx):
    settings = get_project_settings()
    json_file = str(result_path / f'{CommonSpider.domain}_{idx:02d}.jsonl')
    settings.attributes['FEED_URI'].set(json_file, 0)

    crawler = CrawlerProcess(settings)
    crawler.crawl(CommonSpider)
    crawler.start()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--id', required=True)
    args = parser.parse_args()

    settings = get_project_settings()
    json_file = str(result_path / f'{CommonSpider.domain}_{int(args.id):02d}.jsonl')
    settings.attributes['FEED_URI'].set(json_file, 0)

    crawler = CrawlerProcess(settings)
    crawler.crawl(CommonSpider, id=args.id)
    crawler.start()




