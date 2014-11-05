import socket
import sys

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", int(sys.argv[1])))
s.listen(10)

connection, peer = s.accept()
s.close()
while True:
    data = connection.recv(4096)
    if len(data) == 0:
        break
    sys.stdout.write(data)
connection.close()
