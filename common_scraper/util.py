import common_scraper
from pathlib import Path

project_path = Path(common_scraper.__file__).parent.parent

result_path = project_path.joinpath('result')

if __name__ == '__main__':
    print(project_path)
    print(result_path)