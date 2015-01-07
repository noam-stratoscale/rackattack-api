import contextlib
import logging
import time
import os


logger = logging.getLogger('network')


@contextlib.contextmanager
def logNetwork(message):
    transaction = Transaction(message)
    yield
    transaction.finished()


class Transaction:
    def __init__(self, message):
        self._message = message
        self._before = time.time()
        self._unique = _generateUnique()
        logger.debug("Starting '%(message)s' unique '%(unique)s'", dict(
            message=self._message, unique=self._unique))

    def reportState(self, state):
        logger.debug("%(state)s '%(message)s' unique '%(unique)s'", dict(
            message=self._message, unique=self._unique, state=state))

    def finished(self):
        took = time.time() - self._before
        logger.debug("Finished '%(message)s' unique '%(unique)s' took %(took)s", dict(
            message=self._message, unique=self._unique, took=took))
        if took > 0.1:
            logger.error("'%(unique)s' took more than 0.1s: %(took)s", dict(
                unique=self._unique, took=took))
            logging.error("'%(unique)s' took more than 0.1s: %(took)s", dict(
                unique=self._unique, took=took))


def _generateUnique():
    return os.urandom(10).encode('hex')
