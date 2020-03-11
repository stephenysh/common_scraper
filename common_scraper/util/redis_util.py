import redis
from common_scraper.util.cfg_util import db_id

redis_cli = redis.Redis(host='localhost', port=6379, db=db_id, decode_responses=True)



