import re

aleqt_valid_pattern = re.compile(r'\?page=\d+$')
def extract_valid_url(url):
    return aleqt_valid_pattern.sub('', url)