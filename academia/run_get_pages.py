import argparse

from academia.apis import login, downloadPage
from academia.read_books_json import readBooks
from util import getLogger
from util import getRedisClient

parser = argparse.ArgumentParser()
parser.add_argument("--filename", required=True)

args = parser.parse_args()
filename = args.filename

'''
curl "https://academia-arabia.com/Pages/72131/76/${page}/false/1/2" 
-H 'Sec-Fetch-Mode: cors' 
-H 'Sec-Fetch-Site: same-origin' 
-H 'Accept-Language: zh-CN,zh;q=0.9' 
-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36' 
-H 'Accept: */*' 
-H 'Referer: https://academia-arabia.com/Assets/Viewer/oldVersion/build/pdf.worker.js' 
-H 'Sec-Fetch-Dest: empty' 
-H 'Cookie: _ga=GA1.2.355087959.1583647731; _gid=GA1.2.1177952183.1583647731; _culture=en-US; __gads=ID=cdb3a5f28402c03d:T=1583666253:S=ALNI_MaIYp3HDwAT_skRJlxFdrHF5Dfjvw; cb-enabled=accepted; ASP.NET_SessionId=ozkti0ya22cnt5umbxgwj55z; APP-SRV=1; _gat_gtag_UA_23555050_5=1' 
-H 'Connection: keep-alive'
'''
redis_cli = getRedisClient(db=0)

logger = getLogger('Download')

books = readBooks(filename)
books = sorted(books, key=lambda d: d['ORG'])

cookie = login()
if cookie is None:
    exit('log in failed')

for iter_id, book in enumerate(books):
    book_id = book.get('ORG')
    total_pages_num = book.get('NumOfPages')

    logger.info(f'Downloading book {book_id}')

    for page_id in range(1, total_pages_num + 1):
        if redis_cli.get(f'{book_id}:{page_id}') is not None:
            continue

        res = downloadPage(iter_id, book_id, total_pages_num, page_id, cookie,
                           write_dir='/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/academia-pdf')
        if res is True:
            redis_cli.set(f'{book_id}:{page_id}', 1)
