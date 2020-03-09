import configparser

from common_scraper.util import cfg_path
config = configparser.ConfigParser()
config.read(cfg_path)
print(f'reading config from file: {config.sections()}')