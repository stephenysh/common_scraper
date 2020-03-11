import re
import mmap
import redis
import logging
logging.basicConfig(format='[%(asctime)s %(name)s %(filename)s %(funcName)s %(lineno)d %(levelname)s] %(message)s', level=logging.INFO)
import nltk
import itertools
from bs4 import BeautifulSoup
from html import unescape
from string import punctuation

REGPATTERNS = {
    'multi_blank': re.compile('\s+'),
    'html_maybe_text': re.compile(r'^p$|^h[1-6]$|^span$'),
    'arabic_and_space': re.compile('[\u0600-\u06FF ]'),
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


def getRedisClient(host='localhost', port=6379, db=1):
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)


def mostArabicChars(line, threshold=0.8):
    return len(REGPATTERNS['arabic_and_space'].findall(line)) / len(line) > threshold


def arabicCharsRatio(line):
    ratios = range(0, 1, 0.05)
    return len(REGPATTERNS['arabic_and_space'].findall(line)) / len(line)


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
    :return:
    '''
    try:
        soup = BeautifulSoup(response, 'html.parser')

        lines2d = [splitLine(para.get_text()) for para in soup.body.find_all(REGPATTERNS['html_maybe_text'])]

        lines = list(itertools.chain(*lines2d))

        lines = list(set(lines))

        lines = [unescape(line) for line in lines]

        return lines

    except Exception as e:
        logger.error(e)
        return []

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

if __name__ == '__main__':
    print(splitLine('      dasdsad \n fsfsdf \t dsadsad. dasd? da! sd-dasd?    \t\n'))