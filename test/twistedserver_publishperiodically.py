from twisted.internet import reactor
from rackattack.tcp import publish
import threading
import sys
import time


class Do(threading.Thread):
    def __init__(self, pub):
        self._pub = pub
        threading.Thread.__init__(self)
        self.daemon = True
        threading.Thread.start(self)

    def run(self):
        while True:
            time.sleep(0.1)
            self._pub.publish('default topic', dict(data="fake data"))


factory = publish.PublishFactory()
reactor.listenTCP(int(sys.argv[1]), factory)
do = Do(factory)
reactor.run()
