# http://pymotw.com/2/socket/tcp.html

import socket
import sys
import pickle

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print >>sys.stderr, 'Corriendo...'
sock.bind(('', 10000))

while True:
    print >>sys.stderr, 'Esperando conexiones...'
    while True:
        mensaje, remote = sock.recvfrom(10000)
        data = pickle.loads(mensaje)
        print >>sys.stderr, 'Recibido: "%s"' % data, type(data)
