import itertools

import nltk

from util.regex_util import REGPATTERNS


def splitLine(line):
    lines = nltk.sent_tokenize(line)
    lines_2d = [line.split('\n') for line in lines]
    lines = list(itertools.chain(*lines_2d))
    lines = [REGPATTERNS.multi_blank.sub(' ', line.strip()) for line in lines if line.strip() != '']
    return lines
