import re
import urllib.parse

from common_scraper.util.cfg_util import url_prefix

dict_link_pattern = {
    'www.aleqt.com': re.compile(r'\?page=\d+$'),
    'www.albayan.ae': re.compile(r'\?ot=ot\.PrintPageLayout$'),
    'www.al-madina.com': re.compile(r'\?page=\d+$'),
    'www.alittihad.ae': re.compile(r'\.aspx$'),
    'alwatan.com': re.compile(r'\/print\/$'),
    'www.bbc.com': re.compile(r'\?.*$|/\d+$|/\d+\?.*$'),
}

def extract_valid_url(url):
    url = urllib.parse.unquote(url)
    netloc = urllib.parse.urlparse(url_prefix).netloc
    if netloc in dict_link_pattern:
        return dict_link_pattern.get(netloc).sub('', url)
    else:
        return url


want_url_netlocs = {
    "http://autosmea.com/": 1,
    "arabic.arabianbusiness.com": 1
}


def want_url(url) -> bool:
    url_parsed = urllib.parse.urlparse(url)

    if url_parsed.netloc == "arabic.arabianbusiness.com":

        paths = [p for p in url_parsed.path.split("/") if p != '']

        if len(paths) == 2 and paths[0] == "real-estate":

            return True
        else:
            return False
    else:
        return True
