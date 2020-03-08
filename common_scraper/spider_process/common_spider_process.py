import sys
import argparse

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# sys.path.append('/Users/shihangyu/Scripts/python/Scrapers/common_scraper')
from common_scraper.spiders.common_spider import CommonSpider

from common_scraper.util import result_path

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--id', required=True)
    parser.add_argument('--title')
    args = parser.parse_args()

    settings = get_project_settings()
    json_file = str(result_path / f'{CommonSpider.domain}_{int(args.id):02d}.jsonl')
    settings.attributes['FEED_URI'].set(json_file, 0)

    crawler = CrawlerProcess(settings)
    crawler.crawl(CommonSpider, id=args.id, title=args.title)
    crawler.start()


