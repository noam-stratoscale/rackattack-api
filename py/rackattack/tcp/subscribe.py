import threading
import logging
import errno
import socket
from rackattack.tcp import transport


class Subscribe(threading.Thread):
    _SAFE_TERMINATION_ERRORS = [errno.EPIPE, errno.ECONNRESET, errno.ENOTCONN, errno.EBADF]

    def __init__(self, connectTo):
        self._connectTo = connectTo
        self._transport = transport.Transport(connectTo)
        self._registered = dict()
        threading.Thread.__init__(self)
        self.daemon = True
        threading.Thread.start(self)

    def register(self, callback, topic="default topic"):
        assert callback not in self._registered.get(topic, [])
        topicList = self._registered.setdefault(topic, [])
        topicList.append(callback)
        if len(topicList) == 1:
            self._transport.sendJSON(dict(cmd='subscribe', topic=topic))

    def unregister(self, callback, topic="default topic"):
        assert callback in self._registered.get(topic, [])
        topicList = self._registered[topic]
        topicList.remove(callback)
        if len(topicList) == 0:
            self._transport.sendJSON(dict(cmd='unsubscribe', topic=topic))

    def close(self):
        self._transport.close()

    def run(self):
        try:
            logging.info(
                "Rackattack Subscriber started connected to '%(connectTo)s' started",
                dict(connectTo=self._connectTo))
            while not self._transport.closed():
                try:
                    self._work()
                except transport.LocalyClosedError:
                    logging.info("Rackattack subscriber transport closed, locally")
                    return
                except transport.RemotelyClosedError:
                    logging.error("Rackattack subscriber transport closed, remotely")
                    raise
                except socket.error as e:
                    if e.errno not in self._SAFE_TERMINATION_ERRORS:
                        raise
            logging.info("Rackattack subscriber transport closed")
        except:
            logging.exception(
                "Rackattack Subscriber connected to '%(connectTo)s' aborts",
                dict(connectTo=self._connectTo))
            raise

    def _work(self):
        message = self._transport.receiveJSON(timeout=None)
        try:
            for callback in list(self._registered.get(message['topic'])):
                callback(message['arguments'])
        except Exception:
            logging.exception('Handling Published Event')
