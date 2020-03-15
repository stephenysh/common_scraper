from pathlib import Path

exsit_file = Path('/Users/shihangyu/Data/google_input/wiki/wiki.txt')
new_file = Path('/Users/shihangyu/Data/google_input/wiki/wiki_2.txt')

set_exsit = set()
with open(exsit_file, 'rb') as f:
    for line in f:
        line = line.strip()
        if line == '':
            continue

        line = line.decode('utf-8', errors='ignore')
        set_exsit.add(line)

fw_new = open('/Users/shihangyu/Data/google_input/wiki/wiki_2_new.txt', 'w')

fr = open(new_file, 'rb')

for line in fr:
    line = line.strip()
    if line == '':
        continue

    line = line.decode('utf-8', errors='ignore')
    if line not in set_exsit:
        fw_new.write(line + '\n')
