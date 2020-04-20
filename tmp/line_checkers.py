import json
import os
import re
from abc import ABC, abstractmethod

import redis
from bs4 import BeautifulSoup


class AbstractLineChecker(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def __repr__(self):
        return 'AbstractLineChecker'

    @abstractmethod
    def checkline(self, line: str):
        if not line or line == '':
            return False

        return True, line


class ValidJsonLineChecker(AbstractLineChecker):


    def checkline(self, line: str):
        line = line.strip()

        json_obj = json.loads(line)

        # if json_obj['title'] != 'media-49508961':
        #     raise RuntimeWarning('DEBUG WARNING, DO NOT CARE')

        return True, json_obj

    def __repr__(self):
        return 'ValidJsonLineChecker'


class RedisDuplicateLineChecker(AbstractLineChecker):

    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)
        self.r.flushdb()

    def checkline(self, obj: dict):
        title = obj['title']

        try:
            title = re.match(re.compile(rf'(.+)\?page=\d+'), title).group(1)
        except Exception as e:
            pass

        if self.r.get(title) is not None:
            # raise RuntimeError('Redis Duplicate ERROR')
            pass
        else:
            self.r.set(title, 'true')

        return True, obj

    def __repr__(self):
        return 'RedisDuplicateLineChecker'

class ExtracLinesLineChecker(AbstractLineChecker):


    def __init__(self):
        self.split_pattern = re.compile(r'(?<=\w[\.\?\!])[\.\?\!]*\s')
        
        self.may_have_text_pattern = re.compile(r'^p$|^h[1-6]$|^span$')

        self.ar_char_range = re.compile('[\u0600-\u06FF]')

        self.en_char_range = re.compile('[a-zA-Z]')

    def checkline(self, obj: dict):
        response = obj['response']
        title = obj['title']

        title = re.sub(r'\/', '--', title)

        soup = BeautifulSoup(response, 'html.parser')

        pages_dir = '/hdd/result/aleqt_redis_ar_pages'

        os.makedirs(pages_dir, exist_ok=True)

        all_lines = set() # filter duplicate lines in one page
        with open(f'{pages_dir}/{title}.txt', 'w', encoding='utf-8') as fw:
            for p in soup.body.find_all(self.may_have_text_pattern):
                pa = p.get_text().strip()
                if self.check_pa_valid(pa) is False:
                    continue
                lines = re.split(r'\n', pa) # first split by \n
                lines = [re.split(self.split_pattern, line) for line in lines]
                lines = [item for sublist in lines for item in sublist]
                lines = [line for line in lines if self.check_pa_valid(line)]
                lines = [line.strip() +'\n' for line in lines] # writelines dont add line separators, add manually
                all_lines.update(lines)
            fw.writelines(all_lines)

        return True, obj

    def check_pa_valid(self, pa):

        pa = pa.strip()

        if pa == '':
            return False

        if len(pa) < 40:# too short
            return False

        ar_count = re.findall(self.ar_char_range, pa) # has too less of arabic
        if len(ar_count)/len(pa) < 0.7:
            return False

        return True

    def __repr__(self):
        return 'ExtracLinesLineChecker'

