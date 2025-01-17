import socket
import sys
import _thread

MAX_PORT_NUMBER = 65535
PORT = '3490'
DEFAULT_PORT = 3490
BACKLOG = 11
PORT_NUM_PRIME = 64499
DEFAULT_HOST = 'localhost'
UTF_8 = 'utf-8'


class ChatClient:

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self._port = port
        self._host = host
        self._sock = None

    def run(self):
        self.setup_socket_and_connect()
        self.hold_conversation()

    def setup_socket_and_connect(self):

        for result in socket.getaddrinfo(self._host, self._port,
                                         socket.AF_UNSPEC, socket.SOCK_STREAM):
            address_fam, sock_type, proto, cannon_name, sock_address = result
            try:
                self._sock = socket.socket(address_fam, sock_type, proto)
            except socket.error:
                self._sock = None
                continue
            try:
                self._sock.connect(sock_address)
            except socket.error:
                self._sock.close()
                self._sock = None
                continue
            break
        if self._sock is None:
            print("client failed to connect")
            sys.exit(1)

    # TODO: It's very late, but I need to rethink this badly
    def hold_conversation(self):
        self._sock.setblocking(0)
        _thread.start_new_thread(self.listen_conversation, ())
        while 1:
            client_input = input('-->)')
            self._sock.send(client_input.encode())

    def listen_conversation(self):
        while 1:
            try:
                msg = self._sock.recv(1024)
            except socket.error:
                pass
            else:
                msg = msg.decode()
                print('-->' + msg)
