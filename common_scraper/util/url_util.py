import re
import urllib.parse

from common_scraper.util.cfg_util import url_prefix

dict_link_pattern = {
    'www.aleqt.com': re.compile(r'\?page=\d+$'),
    'www.albayan.ae': re.compile(r'\?ot=ot\.PrintPageLayout$'),
}

def extract_valid_url(url):
    netloc = urllib.parse.urlparse(url_prefix).netloc
    if netloc in dict_link_pattern:
        return dict_link_pattern.get(netloc).sub('', url)
    else:
        return url
