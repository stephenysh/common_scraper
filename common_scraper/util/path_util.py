import os
import common_scraper
from pathlib import Path

project_path = Path(common_scraper.__file__).parent.parent

# result_path = project_path.joinpath('result')
result_path = Path('/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/result')
os.makedirs(result_path, exist_ok=True)

job_path = project_path.joinpath('job')
os.makedirs(job_path, exist_ok=True)

cfg_path = project_path.joinpath('scrapy.cfg')


if __name__ == '__main__':
    print(project_path)
    print(result_path)