import logging

logging.basicConfig(format='[%(asctime)s %(filename)s %(lineno)d %(levelname)s] %(message)s', level=logging.INFO)


def getLogger(name):
    return logging.getLogger(name)
