import socket
import sys
import _thread
import select
import queue
import pickle

EMPTY_BYTES_OBJECT_SIZE = 33
PORT = "3490"
DEFAULT_PORT = 3490
BACKLOG = 11
PORT_NUM_PRIME = 64499
UTF_8 = 'utf-8'


class Connection:

    def __init__(self, port, address=None you_host_it=True):
        self.address = address
        self.port = port
        self.you_host_it = you_host_it


class MainServer:

    def __init__(self, port=PORT):
        check_valid_port = int(port)
        if check_valid_port == 0:
            print("invalid port argument")
            exit()
        if check_valid_port < 0 or check_valid_port > 65535:
            print("port number outside of range")
            exit()
        if port != PORT:
            port = check_valid_port
        self._port = port
        self._host = None
        self._sock = None
        self._conn_list = []
        self._seed_dict = {}

    def run(self):
        self.setup_socket_and_listen()
        self.accept_conns_and_serve_msgs()

    def setup_socket_and_listen(self):
        for result in socket.getaddrinfo(self._host, self._port,
                                         socket.AF_UNSPEC,
                                         socket.SOCK_STREAM, 0,
                                         socket.AI_PASSIVE):
            address_fam, sock_type, proto, cannon_name, sock_address = result
            try:
                self._sock = socket.socket(address_fam, sock_type, proto)
                self._sock.setblocking(0)  # for pymotw select implementation
            except socket.error:
                self._sock = None
                continue
            try:
                self._sock.setsockopt(socket.SOL_SOCKET,
                                      socket.SO_REUSEADDR, 1)
            except socket.error as msg:
                print("socket.error: " + str(msg))
                self._sock = None
                sys.exit(1)
            try:
                self._sock.bind(sock_address)
                self._sock.listen(1)
            except socket.error as msg:
                print("socket.error: " + str(msg))
                self._sock.close()
                self._sock = None
                continue
            break
        if self._sock is None:
            print("couldn't open socket")
            sys.exit(1)

    @staticmethod
    def hash_string(string):
        hash = 5381
        for ch in string:
            hash = ((hash << 5) + hash) + ord(ch)

        print(hash % PORT_NUM_PRIME)
        return hash % PORT_NUM_PRIME

    def accept_conns_and_serve_msgs(self):
        msg_queues = {}
        self._conn_list.append(self._sock)

        outputs = []

        while 1:
            readable, writable, exceptional = select.select(self._conn_list,
                                                            self._conn_list,
                                                            self._conn_list)

            if self._sock in readable:
                conn, address = self._sock.accept()
                print("new connection from " + str(address))
                conn.setblocking(0)
                self._conn_list.append(conn)

                msg_queues[conn] = queue.Queue()

            for sock in readable:
                if sock is self._sock:
                    continue
                else:
                    msg = sock.recv(1024)

                    if msg:
                        str_msg = msg.decode()
                        try:
                            int_seed = int(str_msg)
                        except ValueError:
                            print("invalid seed from connection")
                            continue
                        port = self.hash_string(int_seed)
                        existing_connection = self._seed_dict.get(port)
                        if existing_connection is None:
                            address = sock.getpeername()
                            connection = Connection(port, address, False)
                            self._seed_dict[str_msg] = connection
                        else:
                            connection = Connection(port)

















