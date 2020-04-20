import argparse
from pathlib import Path

from util.util import mapLineCharCount

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--pattern')
args = parser.parse_args()

files_path = Path(args.input).resolve()
# total files No:1  total size :11,154,313 total line: 41,000 total chars 6,101,656 average chars per line 148.82
# /hdd/kafka_selenium_google_translate.txt

# total files No:1  total size :985,052,949 total line: 4,198,263 total chars 541,499,745 average chars per line 128.98
# /hdd/all.txt

# total files No:1  total size :140,957,725 total line: 600,259 total chars 77,487,623 average chars per line 129.09
# /hdd/all.test

# files_path = Path('/hdd/result/cleaned_bbc_redis_ar_pages.txt').resolve()


ext = 'json'

if files_path.is_dir():
    assert args.pattern is not None, 'input directory need file pattern'
    files_iter = [file for file in files_path.rglob(args.pattern)]
else:
    files_iter = [files_path]

# fw = open(f'{files_path.parent}/{files_path.name}.{ext}', 'w')

total_size = 0
total_line = 0
total_chars = 0
for file in files_iter:
    lines, bytes, chars, chars_strip = mapLineCharCount(str(file))

    total_size += bytes
    total_line += lines
    total_chars += chars_strip

    print(f'file :{file}  total size :{bytes:,} total line: {lines:,} total chars {chars_strip:,} average chars per line {chars_strip / lines:.2f}')

print(
    f'total files No:{len(files_iter):,}  total size :{total_size:,} total line: {total_line:,} total chars {total_chars:,} average chars per line {total_chars / total_line:.2f}')
