from pathlib import Path

# total files No:617,927  total size :1,620,362,831 total line: 7,495,225
# files_path = Path('/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/result/wiki_redis_ar_pages').resolve()

# total files No:63,326  total size :276,869,207 total line: 1,460,422
# files_path = Path('/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/result/bbc_redis_ar_pages').resolve()

# total files No:63,326  total size :262,714,201 total line: 1,253,388 total chars 143,767,042
# files_path = Path('/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/result/bbc_redis_ar_pages').resolve()

# total files No:1,061,351  total size :2,256,334,164 total line: 15,515,874 total chars 1,230,725,182
# files_path = Path('/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/result/aleqt_redis_ar_pages').resolve()

# total files No:751  total size :109,228,040 total line: 203,632 total chars 59,035,039
# files_path = Path('/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/crawl_sinovision/aawsat').resolve()

# total files No:50,701  total size :1,969,965,012 total line: 5,594,614 total chars 1,066,237,072
# files_path = Path('/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/crawl_sinovision').resolve()

# total files No:1  total size :1,361,056,409 total line: 4,135,779 total chars 744,375,086
# files_path = Path('/home/shihangyu/Scripts/MyScraper/MyScraper/postprocess/sinovision_1.txt').resolve()

# total files No:1  total size :1,334,844,444 total line: 3,986,460 total chars 729,207,669
# files_path = Path('/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/cleaned_crawl_sinovision.txt').resolve()

files_path = Path('/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/cleaned_crawl_sinovision.txt').resolve()


# files_path = Path('/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/result/cleaned_bbc_redis_ar_pages.txt').resolve()


ext = 'txt'

if files_path.is_dir():
    files_iter = files_path.rglob(f'[!count]*.{ext}')
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

print(f'total files No:{total_count:,}  total size :{total_size:,} total line: {total_line:,} total chars {total_chars:,}')
