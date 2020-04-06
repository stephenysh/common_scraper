import itertools
from html import unescape
from typing import Optional, List

from bs4 import BeautifulSoup

from util.log_util import getLogger
from util.nlp_util import splitLine
from util.regex_util import REGPATTERNS

logger = getLogger(__file__)


def htmlResponseToLines(response: str) -> Optional[List[str]]:
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

        lines = list(set(lines))  # deduplicate in one page

        lines = [unescape(line) for line in lines]

        return lines

    except Exception as e:
        logger.error(e)
        return None
