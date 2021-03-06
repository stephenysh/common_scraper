from pathlib import Path

from util.redis_util import getRedisClient


def write_pdf_to_redis():
    redis_cli = getRedisClient(db=0)

    read_path = Path('/hdd/academia-pdf')

    books = read_path.glob("*")
    books = sorted(books, key=lambda p: int(p.name))

    for book in books:
        book_id = book.name
        pages = book.glob("*.pdf")
        pages = sorted(pages, key=lambda p: int(p.stem))

        for page in pages:
            page_id = int(page.stem)

            if page.lstat().st_size <= 0:
                continue
            redis_cli.set(f'{book_id}:{page_id}', 1)


def count_page_num():
    read_path = Path('/hdd/academia-pdf')

    pdfs = read_path.rglob("*.pdf")

    print(len([pdf for pdf in pdfs]))


def count_book_num():
    read_path = Path('/hdd/academia-pdf')

    pdfs = read_path.glob("*")

    print(len([pdf for pdf in pdfs]))


if __name__ == '__main__':
    # count_book_num()
    write_pdf_to_redis()
