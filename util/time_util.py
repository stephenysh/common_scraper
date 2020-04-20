import datetime


def get_utc_timestamp():
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds())


if __name__ == '__main__':
    print(get_utc_timestamp())
