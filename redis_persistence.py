import argparse
import json
import time
from pathlib import Path

from tqdm import tqdm

from util import getRedisClient

parser = argparse.ArgumentParser()
parser.add_argument('--load', action='store_true')
parser.add_argument('--dump', action='store_true')
parser.add_argument('--host', default='localhost')
parser.add_argument('--port', default=6379)
parser.add_argument('--db', required=True)
parser.add_argument('--file', required=True)
args = parser.parse_args()

redis_cli = getRedisClient(host=args.host, port=int(args.port), db=int(args.db))

assert args.load ^ args.dump is True, 'Either dump or load type should be assigned.'

filepath = Path(args.file)

if args.dump:
    assert not filepath.exists(), 'Dump file already exist.'
    print(f'dump into file {filepath}')

    dbsize = redis_cli.dbsize()

    t = time.time()
    with filepath.open('w') as fw:
        for key in tqdm(redis_cli.scan_iter(), total=dbsize):
            d = dict(key=key, value=redis_cli.get(key))
            fw.write(json.dumps(d) + '\n')
    print(f'dump [{dbsize}] keys use time {time.time() - t: .2f}')


else:
    assert filepath.exists(), 'Load file not exist.'
    pass
