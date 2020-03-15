import argparse
import re
from collections import Counter
from pathlib import Path
from pprint import pprint
from string import punctuation

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
args = parser.parse_args()

input_path = Path(args.input)

unwant_chars_list = []

punc = ''.join([rf"\\{i}" for i in punctuation])
unwant_chars_re = re.compile(rf'[^\”\“\«\»\-\–\…\″\’\‘\‑\u202a\u202b\u202c\u202d\u202e\u200b\u200c\u200d\u200e\u200f\u0600-\u06FFa-zA-Z\d '+ punc + ']')

fw = open('unwant.txt', 'w')


d = []
with open(str(input_path), 'r', encoding='utf-8') as fr:
    for line in fr:
        line = line.strip()

        if line == "":
            continue
        if line.endswith('.'):
            d.append('dot_end')
        else:
            if '.' in line:
                d.append('dot_inside_and_not_end')
            else:
                d.append('no_dot')

        chars = re.findall(unwant_chars_re, line)
        if len(chars) > 0:
            fw.write(line + '\n')
            fw.write(' '.join(chars) + '\n')


        unwant_chars_list.extend(chars)

pprint(Counter(unwant_chars_list))
print(sum(Counter(unwant_chars_list).values()))
pprint(Counter(d))