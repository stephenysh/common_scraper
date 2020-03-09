import redis
from common_scraper.cfg_util import config

start_from_scratch = config.get('common_scraper', 'start_from_scratch')

db_id = int(config.get('common_scraper', 'db_id'))

redis_cli = redis.Redis(host='localhost', port=6379, db=db_id, decode_responses=True)

if start_from_scratch == 'True':
    redis_cli.flushdb()
    print(f'flushing redis db {db_id}')


