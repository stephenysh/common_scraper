import json
import re
import random
import math
from util import getLogger
from util import REGPATTERNS
logger = getLogger('line_processors')

def random_pick(line:str):
    '''
    input line , output processed line or None when failed
    :param line:
    :return:
    '''
    try:
        json_obj = json.loads(line)
    except json.JSONDecodeError:
        logger.error('JSONDecodeError')
        return None
    ar_sen = json_obj.get('ar_sen')
    if random.random() > 1/5:
        return None
    if ar_sen is None:
        logger.warning(line)
        return None

    return line

def print_len(line:str):
    '''
    input line , output processed line or None when failed
    :param line:
    :return:
    '''
    try:
        json_obj = json.loads(line)
    except json.JSONDecodeError:
        logger.error('JSONDecodeError')
        return None
    en_sen = json_obj.get('en_sen')
    ar_sen = json_obj.get('ar_sen')

    print(f'arlen: {len(ar_sen.split(" "))} en_sen: {len(en_sen.split(" "))}')

    return None

def random_noise(line:str):
    '''
    input line , output processed line or None when failed
    :param line:
    :return:
    '''
    try:
        json_obj = json.loads(line)
    except json.JSONDecodeError:
        logger.error('JSONDecodeError')
        return None
    en_sen = json_obj.get('en_sen')
    ar_sen = json_obj.get('ar_sen')

    ratio = math.ceil(len(en_sen) / len(ar_sen))

    if random.random() < 0.5:
        ar_rm = 1
    else:
        ar_rm = 2
    en_rm = ar_rm * ratio

    if random.random() < 0.5:
        ar = ' '.join(ar_sen.split(' ')[ar_rm:])
        en = ' '.join(en_sen.split(' ')[en_rm:])
    else:
        ar = ' '.join(ar_sen.split(' ')[:-ar_rm])
        en = ' '.join(en_sen.split(' ')[:-en_rm])

    new_obj = dict(ar_sen=ar, en_sen=en_sen)

    return json.dumps(new_obj, ensure_ascii=False)

def extract_ar_sen(line:str):
    '''
    input line , output processed line or None when failed
    :param line:
    :return:
    '''
    try:
        json_obj = json.loads(line)
    except json.JSONDecodeError:
        logger.error('JSONDecodeError')
        return None
    ar_sen = json_obj.get('ar_sen')

    if ar_sen is None:
        logger.warning(line)
        return None

    return ar_sen

def selenium_only_keep_ar_en_sen(line:str):
    '''
    input line , output processed line or None when failed
    :param line:
    :return:
    '''
    try:
        json_obj = json.loads(line)
    except json.JSONDecodeError:
        logger.error('JSONDecodeError')
        return None
    en_sen = json_obj.get('en_sen')
    ar_sen = json_obj.get('ar_sen')

    if ar_sen is None or en_sen is None or len(en_sen) <10:
        logger.warning(line)
        return None

    new_obj = dict(ar_sen=ar_sen, en_sen=en_sen)

    return json.dumps(new_obj, ensure_ascii=False)

def translate_output_txt2json(line:str):
    '''
    input line , output processed line or None when failed
    :param line:
    :return:
    '''
    split_marks = '######'
    if split_marks not in line:
        return None

    parts = line.split(split_marks)

    if len(parts) != 2 or '' in parts:
        logger.warning(f'split line error: {line}')
        return None

    ar_sen = parts[1]
    en_sen = parts[0]

    new_obj = dict(ar_sen=ar_sen, en_sen=en_sen)

    return json.dumps(new_obj, ensure_ascii=False)