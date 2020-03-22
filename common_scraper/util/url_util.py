import re
import urllib.parse

from common_scraper.util.cfg_util import url_prefix

dict_link_pattern = {
    'www.aleqt.com': re.compile(r'\?page=\d+$'),
    'www.albayan.ae': re.compile(r'\?ot=ot\.PrintPageLayout$'),
    'www.al-madina.com': re.compile(r'\?page=\d+$'),
    'www.alittihad.ae': re.compile(r'\.aspx$'),
    'alwatan.com': re.compile(r'\/print\/$'),
}

def extract_valid_url(url):
    url = urllib.parse.unquote(url)
    netloc = urllib.parse.urlparse(url_prefix).netloc
    if netloc in dict_link_pattern:
        return dict_link_pattern.get(netloc).sub('', url)
    else:
        return url
