import zmq


class Publish:
    def __init__(self, tcpPort):
        self._bindTo = "tcp://127.0.0.1:%d" % tcpPort
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.bind(self._bindTo)

    def allocationChangedState(self, allocationID):
        self._publish(event='allocation__changedState', allocationID=allocationID)

    def _publish(self, ** kwargs):
        self._socket.send_json(kwargs)
