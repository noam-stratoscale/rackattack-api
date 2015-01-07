from twisted.protocols import basic
from twisted.internet import protocol
from twisted.internet import reactor
import struct
import logging
import simplejson


class PublishProtocol(basic.Int32StringReceiver):
    def __init__(self, subscriptions):
        self._subscriptions = subscriptions
        self._mine = []

    def connectionMade(self):
        basic.Int32StringReceiver.connectionMade(self)
        self.transport.setTcpNoDelay(True)

    def stringReceived(self, string):
        try:
            request = simplejson.loads(string)
            topic = request['topic']
            if request['cmd'] == 'subscribe':
                assert topic not in self._mine
                self._mine.append(topic)
                self._subscriptions.setdefault(topic, []).append(self)
            elif request['cmd'] == 'unsubscribe':
                assert topic in self._mine
                self._subscriptions.setdefault(topic, []).remove(self)
                self._mine.remove(topic)
            else:
                raise Exception("Unknown request: %s" % request)
        except:
            logging.exception("Failure handling, aborting connection")
            self.transport.loseConnection()

    def connectionList(self, reason):
        self._unsubscribe()

    def _unsubscribe(self):
        for topic in self._mine:
            self._subscriptions.setdefault(topic, []).remove(self)


class PublishFactory(protocol.Factory):
    _HEADER = "!I"

    def __init__(self):
        self._subscriptions = {}

    def buildProtocol(self, addr):
        return PublishProtocol(self._subscriptions)

    def publish(self, topic, arguments):
        json = simplejson.dumps(dict(topic=topic, arguments=arguments))
        message = self._lengthHeader(len(json)) + json
        reactor.callFromThread(self._publish, topic, message)

    def _publish(self, topic, message):
        for connection in self._subscriptions.get(topic, []):
            connection.transport.write(message)

    def _lengthHeader(self, length):
        return struct.pack(self._HEADER, length)


class Publish:
    def __init__(self, factory):
        self._factory = factory

    def allocationChangedState(self, allocationID):
        self._factory.publish("default topic", dict(
            event='allocation__changedState', allocationID=allocationID))

    def allocationProviderMessage(self, allocationID, message):
        self._factory.publish("default topic", dict(
            event='allocation__providerMessage', allocationID=allocationID, message=message))

    def allocationWithdraw(self, allocationID, message):
        self._factory.publish("default topic", dict(
            event='allocation__withdrawn', allocationID=allocationID, message=message))
