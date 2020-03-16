import signal
import time
from multiprocessing import Pool, cpu_count

def foo(x):
    return x*x

pool = Pool(5)

class GracefulInterruptHandler(object):

    def __init__(self, sig=signal.SIGINT):
        self.sig = sig

    def __enter__(self):

        self.interrupted = False
        self.released = False

        self.original_handler = signal.getsignal(self.sig)

        def handler(signum, frame):
            self.release()
            self.interrupted = True

        signal.signal(self.sig, handler)

        return self

    def __exit__(self, type, value, tb):
        self.release()

    def release(self):

        if self.released:
            return False

        signal.signal(self.sig, self.original_handler)

        self.released = True

        return True


if __name__ == '__main__':
    with GracefulInterruptHandler() as h:
        for i in range(1000):
            print('...')
            time.sleep(1)
            pool.map(foo, [1,2,3,4,5])
            if h.interrupted:
                print("interrupted!")
                time.sleep(2)
                break