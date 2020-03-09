import requests
import time
import json
import logging
logging.basicConfig(format='[%(asctime)s %(name)s %(filename)s %(funcName)s %(lineno)d %(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger('academia-arabic')


def login():
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Origin': 'https://academia-arabia.com',
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'Sec-Fetch-Dest': 'document',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Referer': 'https://academia-arabia.com/Account/Login',
        'Accept-Language': 'en-US,en;q=0.9,mt;q=0.8',

    }

    data = 'Username=IIAI_NLP&UserPassword=iiainlp'

    # try 10 times
    for i in range(10):
        response = requests.post('https://academia-arabia.com/Account/Login', headers=headers, data=data)
        try:
            cookie = response.history[0].headers._store['set-cookie'][1]
            logger.info('log in success!')
            return cookie
        except Exception as e:
            time.sleep(60)

    logger.error('log in failed!')
    return None

def loadTitles(PageNumber, cookie):
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Sec-Fetch-Dest': 'empty',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'Content-Type': 'application/json; charset=UTF-8',
        'Origin': 'https://academia-arabia.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://academia-arabia.com/Browse/Subject',
        'Accept-Language': 'en-US,en;q=0.9,mt;q=0.8',
        'Cookie': cookie
    # ; APP-SRV=1; _ga=GA1.2.1463710133.1583660073; _gid=GA1.2.185659003.1583660073; _culture=en-US; __gads=ID=6d9f577602f140c5:T=1583666253:S=ALNI_MbM-KhYtqIAMlfKrMBAWUd5MhiVKA; hide_survey_popup_permanently=1; hide_survey_popup=1; cb-enabled=accepted; _gat_gtag_UA_23555050_5=1'
    }
    data = {
        'SubjectIDs': [],
        'PageNumber': PageNumber,
        'SortBy': "title asc",
        'TitleSearchTerm': "",
        'Type': "1",
        'accID': "78514"
    }
    # '{SubjectIDs:[],PageNumber:{},SortBy:"title asc",TitleSearchTerm:"",Type:"1",accID:"78514"}'

    response = requests.post('https://academia-arabia.com/api/Browse/LoadMoreTitles', headers=headers, data=json.dumps(data))

    res = json.loads(json.loads(response.content.decode('utf-8')))

    return response.status_code, res['TitleListItemVM']

if __name__ == '__main__':

    cookie = login()

    if cookie is None:
        exit('log in failed')

    idx = 0

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
        for book in book_list:
            id = book.get('ORG')
            if id is None:
                continue

            if id in id_set:
                continue

            id_set.add(id)

            fw.write(json.dumps(book) + '\n')

        idx += 1
