import os
from pathlib import Path

import common_scraper

project_path = Path(common_scraper.__file__).parent.parent

# result_path = project_path.joinpath('result')
result_path = Path('/hdd/crawl_result/english_classification')
os.makedirs(result_path, exist_ok=True)

job_path = project_path.joinpath('job')
os.makedirs(job_path, exist_ok=True)

cfg_path = project_path.joinpath('scrapy.cfg')


if __name__ == '__main__':
    print(project_path)
    print(result_path)