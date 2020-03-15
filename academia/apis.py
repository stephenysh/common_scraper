import json
import os
import time
from pathlib import Path

import requests

from util import getLogger

logger = getLogger('AcademiaApis')

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


def downloadPage(book_id, total_pages_num, page_id, cookie, write_dir='./pdf'):
    book_path = Path(write_dir).resolve().joinpath(str(book_id))
    os.makedirs(str(book_path), exist_ok=True)

    headers = {
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'Accept': '*/*',
        'Referer': 'https://academia-arabia.com/Assets/Viewer/oldVersion/build/pdf.worker.js',
        'Sec-Fetch-Dest': 'empty',
        'Connection': 'keep-alive',
        'Cookie': cookie
    }

    # try 10 times
    for i in range(10):
        try:
            response = requests.post(
                f'https://academia-arabia.com/Pages/{book_id}/{total_pages_num}/{page_id}/false/1/2', headers=headers)
        except:
            headers.update({'Cookie': login()})
            continue

        if response.status_code == 200:
            # check how many zeros should use to fill the page number
            with open(book_path.joinpath(str(page_id).zfill(len(str(total_pages_num))) + '.pdf'), 'wb') as f:
                f.write(response.content)
            logger.info(f'Download Success for book {book_id} at page [{page_id}]/[{total_pages_num}]')
            return True

        headers.update({'Cookie': login()})

    logger.error(f'Download Failed for book {book_id} at page {page_id}: invalid response')

    return False
