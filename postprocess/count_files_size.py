import argparse
from pathlib import Path
from util import mapLineCharCount

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
args = parser.parse_args()

files_path = Path(args.input).resolve()


# files_path = Path('/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/result/cleaned_bbc_redis_ar_pages.txt').resolve()


ext = 'json'

if files_path.is_dir():
    files_iter = [file for file in files_path.rglob(f'*.{ext}')]
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
