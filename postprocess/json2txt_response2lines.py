'''
input one or more json files
json file has keys 'url' 'date' 'response'
extract lines from html of response without any filter or process
and deduplicate global
save to new txt file
'''
import argparse
import json
import time
from multiprocessing import Pool, cpu_count
from pathlib import Path

from util import getLogger, htmlResponseToLines


logger = getLogger('JsonRes2Lines')

def multiHandle(line):
    try:
        json_obj = json.loads(line)
        response = json_obj.get('response')
    except json.JSONDecodeError:
        logger.error('JSONDecodeError')
        return []
    if response is None: return []
    lines = htmlResponseToLines(response)
    return lines

pool = Pool(cpu_count())

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
args = parser.parse_args()
input_str = args.input

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

    fr = open(str(file), 'rb')

    for line in fr:

        line = line.decode('utf-8', errors='ignore').strip()
        #line = line.strip()

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

