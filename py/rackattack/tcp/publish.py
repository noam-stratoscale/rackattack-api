import zmq


class Publish:
    def __init__(self, tcpPort, localhostOnly):
        self._bindTo = "tcp://%s:%d" % ("127.0.0.1" if localhostOnly else "*", tcpPort)
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.bind(self._bindTo)

    def allocationChangedState(self, allocationID):
        self._publish(event='allocation__changedState', allocationID=allocationID)

    def allocationProviderMessage(self, allocationID, message):
        self._publish(event='allocation__providerMessage', allocationID=allocationID, message=message)

    def _publish(self, ** kwargs):
        self._socket.send_json(kwargs)
