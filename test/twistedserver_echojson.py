from twisted.internet import reactor
from rackattack.tcp import transportserver
import sys
import simplejson


class Server:
    def handle(self, string, respondCallback):
        obj = simplejson.loads(string)
        respondCallback(simplejson.dumps(["Echoing", obj]))


server = Server()
factory = transportserver.TransportFactory(server.handle)
reactor.listenTCP(int(sys.argv[1]), factory)
reactor.run()
