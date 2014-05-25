import threading
import zmq
import logging
import simplejson


class IPCServer(threading.Thread):
    def __init__(self, tcpPort, vms, allocator):
        self._vms = vms
        self._allocator = allocator
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._socket.bind("tcp://127.0.0.1:%d" % tcpPort)
        threading.Thread.__init__(self)
        self.daemon = True
        threading.Thread.start(self)

    def _cmd_allocate(self, requirements, allocationInfo):
        allocated = self._allocator.allocate(requirements, allocationInfo)
        result = {}
        for name, vm in allocated.iteritems():
            result[name] = dict(
                id=vm.id(), primaryMACAddress=vm.primaryMACAddress(),
                secondaryMACAddress=vm.secondaryMACAddress(), ipAddress=vm.ipAddress())
        return result

    def _cmd_unallocate(self, id):
###
#not implemented
####
        pass

    def run(self):
        try:
            while True:
                try:
                    self._work()
                except:
                    logging.exception("Handling")
        except:
            logging.exception("Virtual IPC server aborts")
            raise

    def _work(self):
        message = self._socket.recv(0)
        try:
            incoming = simplejson.loads(message)
            handler = getattr(self, "_cmd_" + incoming['cmd'])
            response = handler(** incoming['arguments'])
        except Exception, e:
            logging.exception('Handling')
            response = dict(exceptionString=str(e), exceptionType=e.__class__.__name__)
        self._socket.send_json(response)
