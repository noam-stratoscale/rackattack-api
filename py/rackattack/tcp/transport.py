import socket
import urlparse
import struct
import simplejson
import select
import errno


class TimeoutError(Exception):
    pass


class ClosedError(Exception):
    pass


class LocalyClosedError(ClosedError):
    pass


class RemotelyClosedError(ClosedError):
    pass


class Transport:
    _HEADER = "!I"
    _SAFE_TERMINATION_ERRORS = [errno.EPIPE, errno.ECONNRESET, errno.ENOTCONN, errno.EBADF]

    def __init__(self, uri):
        self._socket = socket.socket()
        try:
            self._socket.connect(self._parseTCPURI(uri))
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except:
            self._socket.close()

    def send(self, data):
        self._socket.send(self._lengthHeader(len(data)) + data)

    def sendJSON(self, obj):
        self.send(simplejson.dumps(obj))

    def receive(self, timeout):
        headerLength = struct.calcsize(self._HEADER)
        header = self._recvAll(headerLength, timeout)
        length = struct.unpack(self._HEADER, header)[0]
        return self._recvAll(length, timeout)

    def receiveJSON(self, timeout):
        payload = self.receive(timeout)
        return simplejson.loads(payload)

    def close(self):
        try:
            self._socket.shutdown(socket.SHUT_WR)
        except socket.error as e:
            if e.errno not in self._SAFE_TERMINATION_ERRORS:
                raise
        try:
            self._socket.shutdown(socket.SHUT_RD)
        except socket.error as e:
            if e.errno not in self._SAFE_TERMINATION_ERRORS:
                raise
        self._socket.close()
        self._socket = None

    def closed(self):
        return self._socket is None

    def _parseTCPURI(self, uri):
        hostname, port = urlparse.urlparse(uri).netloc.split(":")
        return hostname, int(port)

    def _lengthHeader(self, length):
        return struct.pack(self._HEADER, length)

    def _recvAll(self, length, timeout):
        data = ""
        while len(data) < length:
            remains = length - len(data)
            ready, unused, unused = select.select([self._socket], [], [], timeout)
            if len(ready) == 0:
                raise TimeoutError("Timeout while receiving from server (%f seconds)" % timeout)
            sock = self._socket
            if sock is None:
                raise LocalyClosedError("Session closed locally while still receiving")
            segment = sock.recv(remains)
            if len(segment) == 0:
                raise RemotelyClosedError("Peer terminated connection while still receiving")
            data += segment
        return data
