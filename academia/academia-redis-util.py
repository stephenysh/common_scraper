from pathlib import Path

from util import getRedisClient


def write_pdf_to_redis():
    redis_cli = getRedisClient(db=0)

    read_path = Path('/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/academia-pdf')

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


def count_pdf_num():
    read_path = Path('/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/academia-pdf')

    pdfs = read_path.rglob("*.pdf")

    print(len([pdf for pdf in pdfs]))


if __name__ == '__main__':
    write_pdf_to_redis()
