'''
input one or more json files
json file has keys 'url' 'date' 'response'
extract lines from html of response without any filter or process
and deduplicate global
save to new txt file
'''
import json
import time
from pathlib import Path
from util import getLogger, htmlResponseToLines
from multiprocessing import Pool, cpu_count

def multiHandle(line):
    json_obj = json.loads(line)

    response = json_obj.get('response')

    if response is None: return None

    lines = htmlResponseToLines(response)

    return lines

pool = Pool(cpu_count())

logger = getLogger('JsonRes2Lines')

input_str = '/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/result/wam.ae_01.jsonl'

files_path = Path(input_str).resolve()

assert files_path.exists()

if files_path.is_dir():

    fw = open(files_path.parent / f'{files_path.stem}_lines.txt', 'w', encoding='utf-8')

    files = [file for file in files_path.rglob(f'*.json')]
else:

    fw = open(files_path.parent / f'{files_path.stem}_lines.txt', 'w', encoding='utf-8')

    files = [files_path]

logger.info(f'write into file {fw.name}')

lines_set = set()

multi_args = []
for file in files:

    logger.info(f'start file {file}')

    t = time.time()

    fr = open(str(file), 'r', encoding='utf-8')

    for line in fr:

        line = line.strip()

        if line == '': continue

        if len(multi_args) == pool._processes:
            lines2d = pool.starmap(multiHandle, multi_args)
            for lines in lines2d:
                lines_set.update(lines)
            multi_args = []

        multi_args.append((line,))

    if len(multi_args) > 0:
        lines2d = pool.starmap(multiHandle, multi_args)
        for lines in lines2d:
            lines_set.update(lines)
        multi_args = []

    logger.info(f'finish file {file} use time {(time.time() - t):.2f}s')

for line in sorted(lines_set, key=len):
    fw.write(line + '\n')

