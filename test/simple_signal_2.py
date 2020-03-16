import signal
import time
from multiprocessing import Pool, cpu_count, current_process
import sys
import os

def handler(signum, frame):
    print(f'{current_process().name} {os.getpid()} Signal handler called with signal', signum)
    sys.exit(0)

def foo(x):
    # signal.signal(signal.SIGINT, handler)
    return x*x

def init_worker():
    signal.signal(signal.SIGINT, handler)
pool = Pool(5, init_worker)


signal.signal(signal.SIGINT, handler)

while True:
    print('...')
    pool.map(foo, [1,2,3,4,5])
    time.sleep(10)

