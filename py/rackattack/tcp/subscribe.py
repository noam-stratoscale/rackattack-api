import threading
import zmq
import logging
import simplejson


class Subscribe(threading.Thread):
    def __init__(self, connectTo):
        self._connectTo = connectTo
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.SUB)
        self._socket.connect(self._connectTo)
        ALL_MESSAGES = "{"
        self._socket.setsockopt(zmq.SUBSCRIBE, ALL_MESSAGES)
        self._registered = []
        threading.Thread.__init__(self)
        self.daemon = True
        threading.Thread.start(self)

    def register(self, callback):
        assert callback not in self._registered
        self._registered.append(callback)

    def unregister(self, callback):
        assert callback in self._registered
        self._registered.remove(callback)

    def close(self):
        self._socket.close()
        self._context.destroy()

    def run(self):
        try:
            logging.info(
                "Rackattack Subscriber started connected to '%(connectTo)s' started",
                dict(connectTo=self._connectTo))
            while True:
                try:
                    self._work()
                except zmq.ContextTerminated:
                    raise
                except:
                    logging.exception("Handling Published Event")
        except:
            logging.exception(
                "Rackattack Subscriber connected to '%(connectTo)s' aborts",
                dict(connectTo=self._connectTo))
            raise

    def _work(self):
        FLAGS = 0
        message = self._socket.recv(FLAGS)
        try:
            event = simplejson.loads(message)
            for callback in list(self._registered):
                callback(event)
        except Exception:
            logging.exception('Handling Published Event')
