import redis


def getRedisClient(host='localhost', port=6379, db=1):
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

def check_redis_key(db):
    cli = getRedisClient(db=db)

    outs = []
    for key in cli.scan_iter():
        out = key.split("|")[0]
        outs.append(out)

    from collections import Counter
    from pprint import pprint

    pprint(Counter(outs))
    pprint(sorted([(k,v) for k,v in Counter(outs).items()], key=lambda t:t[0]))

def write_redis_to_file(db, filename):
    import json
    cli = getRedisClient(db=db)
    fw = open(filename, "w")
    for key in cli.scan_iter():
        value = cli.get(key)
        d = json.loads(value)
        d['redis_key'] = key
        if value == "":
            continue
        fw.write(json.dumps(d) + '\n')

if __name__ == '__main__':
    check_redis_key(10)