import json
from html import unescape
from typing import Optional, List

from lxml import html

from util.log_util import getLogger

logger = getLogger(__file__)


def htmlResponseToLines(response: str) -> Optional[List[str]]:
    '''
    1. split by nltk and \n
    2. remove continuing blank
    3. deduplicate on one page

    :param response:
    :return: list of lines if success, None if fail
    '''

    json_obj = json.loads(response)

    response = json_obj.get('response')

    try:
        # soup = BeautifulSoup(response, 'html.parser')

        # lines2d = [splitLine(para.get_text()) for para in soup.body.find_all(re.compile(r'^p$|^h[1-6]$|^span$|^a$|^li$'))]

        # lines = list(itertools.chain(*lines2d))

        lines = [l.strip() for l in html.fromstring(response).xpath('//body//text()') if l.strip() != '']

        lines = list(set(lines))  # deduplicate in one page

        lines = [unescape(line) for line in lines]

        return lines

    except Exception as e:
        logger.error(e)
        return None
