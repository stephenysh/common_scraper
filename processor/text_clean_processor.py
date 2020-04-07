from typing import Optional

from util.redis_util import getRedisClient
from util.util import mostArabicChars

redis_cli = getRedisClient(db=15)


def clean_arabic_text(text: str) -> Optional[str]:
    text = text.replace('\\n', '')
    text = text.strip()
    if text == '':
        return None

    if not mostArabicChars(text):
        return None

    if redis_cli.get(text) is not None:
        return None
    else:
        redis_cli.set(text, 'true')
        return text
