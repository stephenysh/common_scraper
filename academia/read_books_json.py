import json
import pickle
from typing import List

from util import getLogger

logger = getLogger('read_books_json')

def readBooks() -> List[dict]:
    '''
    get list of book dict from local json file
    :return:
    '''

    book_id_set = set()

    books = []

    with open('./academia-arabic_id_0.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            try:
                jobj = json.loads(line.strip())
            except json.JSONDecodeError:
                logger.error('JSONDecodeError')
                continue

            if jobj['ORG'] in book_id_set:
                logger.warning(f"duplicate book {jobj['ORG']}")
            else:
                book_id_set.add(jobj['ORG'])
                books.append(jobj)

    return books


if __name__ == '__main__':
    books = readBooks()
    books = sorted(books, key=lambda d: d['ORG'])

    with open('books.pickle', 'wb') as f:
        pickle.dump(books, f)
