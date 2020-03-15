import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
args = parser.parse_args()

files_path = Path(args.input).resolve()


# files_path = Path('/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/result/cleaned_bbc_redis_ar_pages.txt').resolve()


ext = 'txt'

if files_path.is_dir():
    files_iter = [file for file in files_path.rglob(f'*.{ext}')]
else:
    files_iter = [files_path]

# fw = open(f'{files_path.parent}/{files_path.name}.{ext}', 'w')

total_size = 0
total_count = 0
total_line = 0
total_chars = 0
for file in files_iter:
    with open(str(file), 'r', encoding='utf-8') as fr:
        for line in fr:
            line = line.strip()
            if line == '':
                continue
            # fw.write(line + '\n')
            total_line += 1
            total_chars += len(line)

    total_size += file.stat().st_size
    total_count += 1

    if total_count % 10000 == 0:
        print(f'file count: {total_count}')

print(
    f'total files No:{total_count:,}  total size :{total_size:,} total line: {total_line:,} total chars {total_chars:,} average chars per line {total_chars / total_line:.2f}')
