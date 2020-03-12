import json
import logging
logging.basicConfig(format='[%(asctime)s %(name)s %(filename)s %(funcName)s %(lineno)d %(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger('academia-arabic')

from academia.apis import login, loadTitles

if __name__ == '__main__':

    cookie = login()

    if cookie is None:
        exit('log in failed')

    idx = 23341

    fw = open(f'academia-arabic_id_{idx}.jsonl', 'w')

    id_set = set()
    while True:

        # first time failed try to login
        try:
            status_code, book_list = loadTitles(idx, cookie)
        except Exception as e:
            logger.error(f'idx [{idx}] error {e.__class__.__name__}')
            logger.error(e)
            cookie = login()
            if cookie is None:
                exit('log in failed')

        # second time failed continue
        try:
            status_code, book_list = loadTitles(idx, cookie)
        except Exception as e:
            logger.error(f'idx [{idx}] error {e.__class__.__name__}')
            logger.error(e)
            continue

        if status_code != 200:
            logger.warning(f'idx [{idx}] response status [{status_code}]')
            continue

        logger.info(f'idx {idx} success')

        if len(book_list) == 0:
            logger.warning(f'idx [{idx}] has no book')
        for book in book_list:
            id = book.get('ORG')
            if id is None:
                continue

            if id in id_set:
                continue

            id_set.add(id)

            fw.write(json.dumps(book) + '\n')

        idx += 1
