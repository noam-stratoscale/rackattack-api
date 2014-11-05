import select
import threading
import logging
import os
from rackattack.ssh import tunnellocalforwardingserver


class Tunnel(threading.Thread):
    def __init__(self, openDirectTCPIPChannelCallback):
        self._openDirectTCPIPChannelCallback = openDirectTCPIPChannelCallback
        self._logger = logging.getLogger('ssh')
        self._workers = []
        self._pleaseCloseWorkers = False
        self._closed = False
        self._readFD, self._writeFD = os.pipe()
        threading.Thread.__init__(self)
        self.daemon = True
        threading.Thread.start(self)

    def localForward(self, remoteEndpoint):
        "remoteEndpoint is (hostname, port) or just port for localhost"
        forwarder = tunnellocalforwardingserver.TunnelLocalForwardingServer(
            openDirectTCPIPChannelCallback=self._openDirectTCPIPChannelCallback,
            addConnectionCallback=self._addConnection,
            remoteEndpoint=remoteEndpoint)
        self._workers.append(forwarder)
        self._wakeUp()
        return forwarder.port()

    def manyLocalForwards(self, remoteEndpoints):
        for endpoint in remoteEndpoints:
            self.localForward(endpoint)

    def stopAll(self):
        self._pleaseCloseWorkers = True
        self._wakeUp()

    def close(self):
        self._closed = True
        self._wakeUp()

    def run(self):
        try:
            while not self._closed:
                self._work()
        finally:
            self._closeWorkers()
            os.close(self._readFD)
            os.close(self._writeFD)

    def _wakeUp(self):
        os.write(self._writeFD, "X")

    def _selectableSockets(self):
        return sum([w.selectableSockets() for w in self._workers], []) + [self._readFD]

    def _work(self):
        r, w, e = select.select(self._selectableSockets(), [], [])
        for worker in list(self._workers):
            worker.work(r)
            if worker.done():
                worker.close()
                self._workers.remove(worker)
        if self._readFD in r:
            os.read(self._readFD, 1)
        if self._pleaseCloseWorkers:
            self._pleaseCloseWorkers = False
            self._closeWorkers()

    def _closeWorkers(self):
        while len(self._workers) > 0:
            worker = self._workers.pop(0)
            worker.close()

    def _addConnection(self, connection):
        self._workers.append(connection)
        self._wakeUp()
