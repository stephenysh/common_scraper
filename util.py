import json
import logging
import mmap
import re
import time

import redis

logging.basicConfig(format='[%(asctime)s %(name)s %(filename)s %(funcName)s %(lineno)d %(levelname)s] %(message)s', level=logging.INFO)
import nltk
import itertools
from bs4 import BeautifulSoup
from html import unescape
from string import punctuation
from bisect import bisect_left

REGPATTERNS = {
    'multi_blank': re.compile('\s+'),
    'html_maybe_text': re.compile(r'^p$|^h[1-6]$|^span$'),
    'arabic_chars_and_space': re.compile('[\u0600-\u06FF ]'),
    'english_chars_and_space': re.compile('[a-zA-Z ]'),
    'arabic_chars': re.compile('[\u0600-\u06FF]'),
    'english_chars': re.compile('[a-zA-Z]'),
    'arabic_words': re.compile('[\u0600-\u06FF]+'),
    'bad_chars': re.compile(rf'[^\”\“\«\»\-\–\…\″\’\‘\‑\u202a\u202b\u202c\u202d\u202e\u200b\u200c\u200d\u200e\u200f\u0600-\u06FFa-zA-Z\d '+ ''.join([rf"\\{i}" for i in punctuation]) + ']+')
}

def getLogger(name):

    return logging.getLogger(name)

logger = getLogger('Util')

def mapLineCount(filename):
    try:
        f = open(filename, "r+")
        buf = mmap.mmap(f.fileno(), 0)
        lines = 0
        readline = buf.readline
        while readline():
            lines += 1
        return lines
    except:
        return 0

def mapLineCharCount(filename):
    try:
        f = open(filename, "r+")
        buf = mmap.mmap(f.fileno(), 0)
        lines = 0
        bytes = 0
        chars = 0
        chars_strip = 0
        while True:
            line = buf.readline()
            if not line:
                break
            bytes += len(line)
            line = line.decode('utf-8', errors='ignore')
            chars += len(line)
            chars_strip += len(line.strip())
            lines += 1
        return lines, bytes, chars, chars_strip
    except Exception as e:
        return 0, 0, 0, 0

def getRedisClient(host='localhost', port=6379, db=1):
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)


def mostArabicChars(line, threshold=0.8):
    return len(REGPATTERNS['arabic_and_space'].findall(line)) / len(line) > threshold


def arabicCharsRatio(line):
    ratios = [i / 100 for i in range(5, 100 + 5, 5)]
    ratio = len(REGPATTERNS['arabic_and_space'].findall(line)) / len(line)
    return ratios[bisect_left(ratios, ratio)]


def arabicWordsNumLimit(line, min_len=5, max_len=100):
    length = len(REGPATTERNS['arabic_words'].findall(line))
    return min_len <= length <= max_len


def arabicWordsNum(line):
    return len(REGPATTERNS['arabic_words'].findall(line))

def splitLine(line):
    lines = nltk.sent_tokenize(line)
    lines_2d = [line.split('\n') for line in lines]
    lines = list(itertools.chain(*lines_2d))
    lines = [REGPATTERNS['multi_blank'].sub(' ', line.strip()) for line in lines if line.strip() != '']
    return lines


def hasBadPhrases(line):
    return not any(substring in line for substring in ['css', 'CSS', '<'])

def hasBadChars(line):
    return len(REGPATTERNS['bad_chars'].findall(line)) > 0

def htmlResponseToLines(response: str):
    '''
    1. split by nltk and \n
    2. remove continuing blank
    3. deduplicate on one page

    :param response:
    :return: list of lines if success, None if fail
    '''
    try:
        soup = BeautifulSoup(response, 'html.parser')

        lines2d = [splitLine(para.get_text()) for para in soup.body.find_all(REGPATTERNS['html_maybe_text'])]

        lines = list(itertools.chain(*lines2d))

        lines = list(set(lines)) # deduplicate in one page

        lines = [unescape(line) for line in lines]

        return lines

    except Exception as e:
        logger.error(e)
        return None

def filterLineRecord(idx, line) -> dict:
    res = {}

    # filter no end dot sentences
    if line.endswith('.'):
        res.update(endWithDot=idx)

    # filter unwanted chars
    if hasBadPhrases(line):
        res.update(hasBadPhrases=idx)

    # filter by not any non arabic chars unwant_chars_re
    if hasBadChars(line):
        res.update(hasBadChars=idx)

    # # filter by arabic word length
    # if arabicWordsNumLimit(line):
    #     res.update(arabicWordsNumLimit=idx)
    #
    # # filter non arabic
    # if mostArabicChars(line):
    #     res.update(mostArabicChars=idx)

    # filter by arabic word length
    res.update(arabicWordsNum={arabicWordsNum(line): idx})

    # filter non arabic
    res.update(arabicCharsRatio={arabicCharsRatio(line): idx})

    return res


def write_redis_to_file(filename, host='localhost', port=6379, db=0):
    redis_cli = getRedisClient(host=host, port=port, db=db)

    with open(filename, 'w') as fw:
        count = 0
        t = time.time()
        for key in redis_cli.scan_iter():
            d = dict(key=key, value=redis_cli.get(key))
            fw.write(json.dumps(d) + '\n')
            count += 1
    print(f'total keys {count}')
    print(f'scan keys use time {time.time() - t}')

    t = time.time()
    print(f'db size {redis_cli.dbsize()}')
    print(f'dbsize use time {time.time() - t}')


def read_file_to_redis(filename, host='localhost', port=6379, db=0):
    redis_cli = getRedisClient(host=host, port=port, db=db)

    t = time.time()
    with open(filename, 'rb') as fr:
        for line_count, line in enumerate(fr):
            line = line.decode('utf-8', errors='ignore')
            line = line.strip()

            try:
                json_obj = json.loads(line)
            except json.JSONDecodeError:
                print('Json Decode Error')
                continue

            key = json_obj.get('key')
            value = json_obj.get('value')

            if None in [key, value]:
                print('Null in key or value')
                continue

            redis_cli.set(key, value)

    print(f'line count {line_count}')
    print(f'db size {redis_cli.dbsize()}')
    print(f'insert use time {time.time() - t}')

if __name__ == '__main__':
    print(splitLine('      dasdsad \n fsfsdf \t dsadsad. dasd? da! sd-dasd?    \t\n'))
