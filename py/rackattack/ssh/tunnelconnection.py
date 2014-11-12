import socket
import logging


class TunnelConnection:
    def __init__(self, socket, channel):
        self._socket = socket
        self._channel = channel
        self._logger = logging.getLogger('ssh')
        self._shutdownToRemote = False
        self._shutdownFromRemote = False

    def done(self):
        return self._shutdownFromRemote and self._shutdownToRemote

    def close(self):
        if not self.done():
            self._logger.debug("Shutting down SSH tunneling connection due script request")
        if not self._shutdownFromRemote:
            self._socket.shutdown(socket.SHUT_WR)
            self._shutdownFromRemote = True
        if not self._shutdownToRemote:
            self._channel.shutdown(socket.SHUT_WR)
            self._shutdownToRemote = True
        if self._channel is not None:
            self._channel.close()
            self._channel = None
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def selectableSockets(self):
        assert not self.done()
        if self._shutdownFromRemote and not self._shutdownToRemote:
            return [self._socket]
        elif not self._shutdownFromRemote and self._shutdownToRemote:
            return [self._channel]
        else:
            return [self._socket, self._channel]

    def work(self, readReadySockets):
        assert not self.done()
        self._workFromRemote(readReadySockets)
        self._workToRemote(readReadySockets)

    def _workFromRemote(self, readReadySockets):
        if self._shutdownFromRemote:
            assert self._channel not in readReadySockets
            return
        if self._channel in readReadySockets:
            data = self._channel.recv(2048)
            if len(data) == 0:
                self._shutdownFromRemote = True
                self._socket.shutdown(socket.SHUT_WR)
                self._logger.debug("SSH forward channel got shutdown from remote")
                if self.done():
                    self._logger.debug("Both ends shutdown, closing connection")
                    self.close()
            else:
                self._socket.send(data)

    def _workToRemote(self, readReadySockets):
        if self._shutdownToRemote:
            assert self._socket not in readReadySockets
            return
        if self._socket in readReadySockets:
            data = self._socket.recv(2048)
            if len(data) == 0:
                self._shutdownToRemote = True
                self._channel.shutdown(socket.SHUT_WR)
                self._logger.debug("SSH forward channel got shutdown from local")
                if self.done():
                    self._logger.debug("Both ends shutdown, closing connection")
                    self.close()
            else:
                self._channel.send(data)
