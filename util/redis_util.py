import redis


def getRedisClient(host='localhost', port=6379, db=1):
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)
