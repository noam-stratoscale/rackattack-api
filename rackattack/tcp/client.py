import zmq
from rackattack import api
import threading
from rackattack.tcp import node


class Client(api.Client):
    def __init__(self, connectTo):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)
        self._socket.connect(connectTo)
        self._socket.setsockopt(zmq.LINGER, 0)
        self._lock = threading.Lock()

    def allocate(self, requirements, allocationInfo, forceReleaseCallback):
        assert len(requirements) > 0
        jsonableRequirements = {
            name: requirement.__dict__ for name, requirement in requirements.iteritems()}
        allocatedMap = self.call(
            cmd='allocate',
            requirements=jsonableRequirements,
            allocationInfo=allocationInfo.__dict__)
        result = {}
        for name, allocated in allocatedMap.iteritems():
            nodeInstance = node.Node(ipcClient=self, name=name, allocated=allocated)
            result[name] = nodeInstance
        return result

    def call(self, cmd, ipcTimeoutMS=3000, ** kwargs):
        with self._lock:
            return self._call(cmd, ipcTimeoutMS, kwargs)

    def _call(self, cmd, ipcTimeoutMS, arguments):
        self._socket.send_json(dict(cmd=cmd, arguments=arguments))
        hasData = self._socket.poll(ipcTimeoutMS)
        if not hasData:
            self._context.destroy()
            raise Exception("IPC command '%s' timed out" % cmd)
        result = self._socket.recv_json()
        if isinstance(result, dict) and 'exceptionType' in result:
            if result['exceptionType'] == 'NotEnoughResourcesForAllocation':
                raise api.NotEnoughResourcesForAllocation(result['exceptionString'])
            else:
                raise Exception("IPC command '%s' failed: %s: '%s'" % (
                    cmd, result['exceptionType'], result['exceptionString']))
        return result
