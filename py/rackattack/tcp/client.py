import zmq
from rackattack import api
import threading
from rackattack.tcp import allocation
from rackattack.tcp import heartbeat
from rackattack.tcp import subscribe


class Client(api.Client):
    def __init__(self, providerRequestLocation, providerSubscribeLocation):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)
        self._socket.connect(providerRequestLocation)
        self._socket.setsockopt(zmq.LINGER, 0)
        self._lock = threading.Lock()
        self.call("handshake", versionInfo=dict(
            RACKATTACK_VERSION=api.VERSION,
            ZERO_MQ=dict(
                PYZMQ_VERSION=zmq.pyzmq_version(),
                VERSION=zmq.VERSION,
                VERSION_MAJOR=zmq.VERSION_MAJOR,
                VERSION_MINOR=zmq.VERSION_MINOR,
                VERSION_PATCH=zmq.VERSION_PATCH)))
        self._subscribe = subscribe.Subscribe(connectTo=providerSubscribeLocation)
        self._heartbeat = heartbeat.HeartBeat(self)

    def allocate(self, requirements, allocationInfo):
        assert len(requirements) > 0
        jsonableRequirements = {
            name: requirement.__dict__ for name, requirement in requirements.iteritems()}
        allocationID = self.call(
            cmd='allocate',
            requirements=jsonableRequirements,
            allocationInfo=allocationInfo.__dict__)
        return allocation.Allocation(
            id=allocationID, requirements=requirements, ipcClient=self,
            subscribe=self._subscribe, heartbeat=self._heartbeat)

    def call(self, cmd, ipcTimeoutMS=3000, ** kwargs):
        with self._lock:
            return self._call(cmd, ipcTimeoutMS, kwargs)

    def _call(self, cmd, ipcTimeoutMS, arguments):
        self._socket.send_json(dict(cmd=cmd, arguments=arguments))
        hasData = self._socket.poll(ipcTimeoutMS)
        if not hasData:
            self._context.destroy()
            raise Exception("IPC command '%s' timed out" % cmd)
        result = self._socket.recv_json(zmq.NOBLOCK)
        if isinstance(result, dict) and 'exceptionType' in result:
            if result['exceptionType'] == 'NotEnoughResourcesForAllocation':
                raise api.NotEnoughResourcesForAllocation(result['exceptionString'])
            else:
                raise Exception("IPC command '%s' failed: %s: '%s'" % (
                    cmd, result['exceptionType'], result['exceptionString']))
        return result
