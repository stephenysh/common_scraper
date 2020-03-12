'''
filter data from one .txt files
return dict record
'''

import argparse
from multiprocessing import Pool
from pathlib import Path

from util import *

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
args = parser.parse_args()

files_path = Path(args.input).resolve()

assert files_path.exists()

ext = 'txt'

if files_path.is_dir():
    files_iter = [file for file in files_path.rglob(f'*.{ext}')]
else:
    files_iter = [files_path]

pool_size = 1 #multiprocessing.cpu_count() * 12
pool = Pool(pool_size)

record = {}

for file in files_iter:
    print(file)
    read_line_count = 0
    read_lines_total = mapLineCount(str(file))
    # read_lines_total = 0
    map_args = []
    with open(str(file), 'r', encoding='utf-8') as fr:
        for line in fr:
            line = line.strip()

            if line == '':
                continue

            if len(map_args) == pool_size:
                dicts = pool.starmap(filterLineRecord, map_args)
                for d in dicts:
                    for k, v in d.items():
                        if isinstance(v, int):
                            record.setdefault(k, []).append(v)
                        elif isinstance(v, dict):
                            for kk, vv in v.items():
                                record.setdefault(k, {}).setdefault(kk, []).append(vv)
                        else:
                            raise RuntimeError('Invalid type of value')
                map_args = []

            map_args.append((read_line_count, line,))

            read_line_count += 1

            if read_line_count % 10000 == 0:
                print(f'lines [{read_line_count: ,}]/[{read_lines_total: ,}]')

for k in sorted(record.keys()):
    v = record[k]
    if isinstance(v, list):
        print(f'{k:<50}:{len(v): ,}/{len(v) / read_line_count:.6f}')
    elif isinstance(v, dict):
        for kk in sorted(v.keys()):
            print(f'{k}:{kk}: {len(v[kk]): ,}/{len(v[kk]) / read_line_count:.6f}')
    else:
        raise RuntimeError('Invalid type of value')




#
#
#
# if files_path.is_dir():
#     files_iter = files_path.rglob(f'*.{ext}')
#     fw = open(files_path.parent / f'cleaned_{files_path.name}.{ext}', 'w', encoding='utf-8')
# else:
#     files_iter = [files_path]
#     fw = open(files_path.parent / f'cleaned_{files_path.name}', 'w', encoding='utf-8')
#
# for line in sorted(sen_set, key=len):
#     fw.write(line + '\n')