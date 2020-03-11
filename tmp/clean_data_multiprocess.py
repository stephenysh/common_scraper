'''
clean data from one or more .txt files
'''

import re
from pathlib import Path
import nltk
import mmap
import multiprocessing
from multiprocessing import Pool
import itertools
from string import punctuation
from util import mapLineCount


split_pattern = re.compile(r'(?<=\w[\.\?\!])[\.\?\!]*\s')
ar_word_pattern = re.compile('[\u0600-\u06FF]+')
ar_char_and_space_pattern = re.compile('[\u0600-\u06FF ]')
non_ar_char_pattern = re.compile('[^\u0600-\u06FF ]')
mul_space_pattern = re.compile('\s+')
punc = ''.join([rf"\\{i}" for i in punctuation])
unwant_chars_re = re.compile(rf'[^\”\“\«\»\-\–\…\″\’\‘\‑\u202a\u202b\u202c\u202d\u202e\u200b\u200c\u200d\u200e\u200f\u0600-\u06FFa-zA-Z\d '+ punc + ']+')
valid_line_end_punc_re = '^.*[\.\?\!]$'

# input_str = '/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/crawl_sinovision.txt'
# input_str = '/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/result/bbc_redis_ar_pages'
# input_str = '/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/result/aleqt_redis_ar_pages'
input_str = '/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/result/wiki_redis_ar_pages'


files_path = Path(input_str).resolve()

assert files_path.exists()

ext = 'txt'

if files_path.is_dir():
    files_iter = files_path.rglob(f'*.{ext}')
    fw = open(files_path.parent / f'cleaned_{files_path.name}.{ext}', 'w', encoding='utf-8')
else:
    files_iter = [files_path]
    fw = open(files_path.parent / f'cleaned_{files_path.name}', 'w', encoding='utf-8')


def handle_per_line(line):
    # remove multiple space
    line = re.sub(mul_space_pattern, ' ', line)

    # maybe split by dot
    # lines = re.split(split_pattern, line)
    lines = nltk.sent_tokenize(line)

    # filter no end dot sentences
    # lines = [line for line in lines if line.endswith('.')]

    # filter unwanted chars
    lines = [line for line in lines if not any(substring in line for substring in ['css', 'CSS', '<'])]

    # filter by arabic word length
    lines = [line for line in lines if len(ar_word_pattern.findall(line)) >= 10 and len(ar_word_pattern.findall(line)) <= 100]

    # filter non arabic
    lines = [line for line in lines if (len(re.findall(ar_char_and_space_pattern, line)) / len(line)) > 0.9]

    # # filter by not any non arabic chars unwant_chars_re
    lines = [line for line in lines if len(unwant_chars_re.findall(line)) == 0]

    # deduplicate use set
    lines = [line for line in lines if not line in sen_set]
    return lines

result_line_count = 0
result_char_count = 0
sen_set = set()

pool_size = multiprocessing.cpu_count() * 12
pool = Pool(pool_size)


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
                lines_2d = pool.starmap(handle_per_line, map_args)
                map_args = []
                lines = list(itertools.chain(*lines_2d))
                sen_set.update(lines)
                result_line_count += len(lines)
                result_char_count += sum([len(line) for line in lines])

            map_args.append((line,))

            # fw.write('|'.join([line]) + '\n')
            read_line_count += 1


            if read_line_count % 10000 == 0:
                print(f'lines [{read_line_count: ,}]/[{read_lines_total: ,}]')

        print(len(sen_set))



for line in sorted(sen_set, key=len):
    fw.write(line + '\n')

print(f'lines: {result_line_count: ,} chars: {result_char_count: ,}')