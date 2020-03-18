from multiprocessing import Pool, cpu_count


class PoolWrapper:

    def __init__(self, func: callable, poolsize=cpu_count()):
        self.pool = Pool(poolsize)

        self.args = []

        self.func = func

    def addSample(self, *sample):
        '''
        append parameters as tuple cause starmap receive tuple arguments
        :param sample:
        :return:
        '''
        self.args.append(sample)

    def maybeProcessIfFull(self):
        res = []
        processed = False
        if len(self.args) == self.getPoolSize():
            res = self.pool.starmap(self.func, self.args)
            self.args = []
            processed = True
        return processed, res

    def mustProcessUnlessEmpty(self):
        res = []
        processed = False
        if len(self.args) > 0:
            res = self.pool.starmap(self.func, self.args)
            self.args = []
            processed = True
        return processed, res

    def getPoolSize(self):
        return self.pool._processes
