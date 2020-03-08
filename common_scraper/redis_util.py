import redis
redis_cli = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
redis_cli.flushdb()