import redis


def getRedisClient(host='localhost', port=6379, db=1):
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

def check_redis_key():
    cli = getRedisClient(db=8)

    outs = []
    for key in cli.scan_iter():
        out = key.split("|")[0]
        outs.append(out)

    from collections import Counter
    from pprint import pprint

    pprint(Counter(outs))
    pprint(sorted([(k,v) for k,v in Counter(outs).items()], key=lambda t:t[0]))

if __name__ == '__main__':
    check_redis_key()