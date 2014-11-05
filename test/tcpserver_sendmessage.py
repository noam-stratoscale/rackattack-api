import socket
import sys

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", int(sys.argv[1])))
s.listen(10)

while True:
    connection, peer = s.accept()
    connection.send(sys.argv[2])
    connection.close()
