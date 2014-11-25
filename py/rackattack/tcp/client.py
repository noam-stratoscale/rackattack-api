import zmq
from rackattack import api
import threading
from rackattack.tcp import allocation
from rackattack.tcp import heartbeat
from rackattack.tcp import subscribe
from rackattack.tcp import suicide
import logging
import urllib2


class Client(api.Client):
    def __init__(self,
                 providerRequestLocation,
                 providerSubscribeLocation,
                 providerHTTPLocation):
        self._providerHTTPLocation = providerHTTPLocation
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)
        self._socket.connect(providerRequestLocation)
        self._socket.setsockopt(zmq.LINGER, 0)
        self._lock = threading.Lock()
        self._closed = False
        self._activeAllocations = []
        self.call("handshake", versionInfo=dict(
            RACKATTACK_VERSION=api.VERSION,
            ZERO_MQ=dict(
                PYZMQ_VERSION=zmq.pyzmq_version(),
                VERSION=zmq.VERSION,
                VERSION_MAJOR=zmq.VERSION_MAJOR,
                VERSION_MINOR=zmq.VERSION_MINOR,
                VERSION_PATCH=zmq.VERSION_PATCH)))
        self._subscribe = subscribe.Subscribe(connectTo=providerSubscribeLocation)
        self._connectionToProviderInterrupted = suicide.killSelf
        self._heartbeat = heartbeat.HeartBeat(self)

    def allocate(self, requirements, allocationInfo):
        assert len(requirements) > 0
        jsonableRequirements = {
            name: requirement.__dict__ for name, requirement in requirements.iteritems()}
        allocationID = self.call(
            cmd='allocate',
            requirements=jsonableRequirements,
            allocationInfo=allocationInfo.__dict__)
        allocationInstance = allocation.Allocation(
            id=allocationID, requirements=requirements, ipcClient=self,
            subscribe=self._subscribe, heartbeat=self._heartbeat)
        self._activeAllocations.append(allocationInstance)
        return allocationInstance

    def call(self, cmd, ipcTimeoutMS=3000, ** kwargs):
        try:
            with self._lock:
                if self._closed:
                    raise Exception("Already closed")
                return self._call(cmd, ipcTimeoutMS, kwargs)
        except:
            self._notifyAllActiveAllocationsThatConnectionToProviderInterrupted()
            raise

    def urlopen(self, path):
        url = self._providerHTTPLocation.rstrip("/") + "/" + path.lstrip("/")
        return urllib2.urlopen(url)

    def _call(self, cmd, ipcTimeoutMS, arguments):
        self._socket.send_json(dict(cmd=cmd, arguments=arguments))
        hasData = self._socket.poll(ipcTimeoutMS)
        if not hasData:
            self._closeLocked()
            raise Exception("IPC command '%s' timed out" % cmd)
        result = self._socket.recv_json(zmq.NOBLOCK)
        if isinstance(result, dict) and 'exceptionType' in result:
            if result['exceptionType'] == 'NotEnoughResourcesForAllocation':
                raise api.NotEnoughResourcesForAllocation(result['exceptionString'])
            else:
                raise Exception("IPC command '%s' failed: %s: '%s'" % (
                    cmd, result['exceptionType'], result['exceptionString']))
        return result

    def close(self):
        with self._lock:
            assert len(self._activeAllocations) == 0
            self._closeLocked()

    def _closeLocked(self):
        if self._closed:
            return
        self._closed = True
        if hasattr(self, '_subscribe'):
            self._subscribe.close()
        self._socket.close()
        self._context.destroy()

    def heartbeatFailed(self):
        self._notifyAllActiveAllocationsThatConnectionToProviderInterrupted()
        self.close()
        self._connectionToProviderInterrupted()

    def _notifyAllActiveAllocationsThatConnectionToProviderInterrupted(self):
        for allocationInstance in list(self._activeAllocations):
            allocationInstance.connectionToProviderInterrupted()
        assert len(self._activeAllocations) == 0

    def setConnectionToProviderInterruptedCallback(self, callback):
        self._connectionToProviderInterrupted = callback

    def allocationClosed(self, allocationInstance):
        self._activeAllocations.remove(allocationInstance)
