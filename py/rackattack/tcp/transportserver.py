from twisted.protocols import basic
from twisted.internet import protocol
from twisted.internet import reactor
import struct
import logging


class TransportProtocol(basic.Int32StringReceiver):
    MAX_LENGTH = 4096
    _HEADER = "!I"

    def __init__(self, handler):
        self._handler = handler

    def connectionMade(self):
        basic.Int32StringReceiver.connectionMade(self)
        self.transport.setTcpNoDelay(True)

    def stringReceived(self, string):
        try:
            self._handler(string, self._respond, self.transport.socket.getpeername())
        except:
            logging.exception("Failure handling, aborting connection")
            self.transport.loseConnection()

    def _lengthHeader(self, length):
        return struct.pack(self._HEADER, length)

    def _respond(self, response):
        header = self._lengthHeader(len(response))
        reactor.callFromThread(self._respondFromThread, header + response)

    def _respondFromThread(self, message):
        self.transport.write(message)


class TransportFactory(protocol.Factory):
    def __init__(self, handler):
        self._handler = handler

    def buildProtocol(self, addr):
        return TransportProtocol(self._handler)
