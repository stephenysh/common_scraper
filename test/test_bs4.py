import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

files_path = Path('/hdd/result/bbc_redis_ar_jsons').resolve()
ext = '.json'


linecount_total = 0
charcount_total = 0

global_min = sys.maxsize
global_max = -1

for file in files_path.iterdir():
    if not file.name.endswith(ext):
        continue

    print(f'reading file {file}')
    with open(str(file), 'r', encoding='utf-8') as fr:
        while True:

            try:
                line = fr.readline().strip()

                if not line:
                    break

                json_obj = json.loads(line)

                response = json_obj['response']

                soup = BeautifulSoup(response, 'html.parser')

                elements = soup.body.find_all(re.compile(r'^div$'), attrs={'class': 'date date--v2'})

                tmp_list = [int(elem.attrs['data-seconds']) for elem in elements]
                if len(tmp_list) == 0:
                    continue
                tmp_max = max(tmp_list)
                tmp_min = min(tmp_list)

                global_max = tmp_max if tmp_max > global_max else global_max
                global_min = tmp_min if tmp_min < global_min else global_min
            except Exception as e:
                print(f'ERROR: {e}')

    print(global_max)
    print(global_min)
