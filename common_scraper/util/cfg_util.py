import configparser

from common_scraper.util.path_util import cfg_path
config = configparser.ConfigParser()
config.read(cfg_path)
print(f'reading config from file: {config.sections()}')

start_from_scratch = config.get('common_scraper', 'start_from_scratch')

db_id = int(config.get('common_scraper', 'db_id'))

url_prefix = config.get('common_scraper', 'url_prefix')

url_name = config.get('common_scraper', 'url_name')