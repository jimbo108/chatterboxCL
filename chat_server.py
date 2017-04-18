import socket
import sys
import _thread
import select
import queue

EMPTY_BYTES_OBJECT_SIZE = 33
PORT = "3490"
DEFAULT_PORT = 3490
BACKLOG = 11
PORT_NUM_PRIME = 64499
UTF_8 = 'utf-8'


class ChatServer:

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
        self._running_uid = 0
        self._conn_list = []

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

    # Method adapted (taken) from https://pymotw.com/2/select
    # UNFINISHED
    def accept_conns_and_serve_msgs(self):
        msg_queues = {}
        self._conn_list.append(self._sock)  # this isn't great but it seems
                                            # cleaner than the alternatives
        outputs = []

        while 1:
            readable, writable, exceptional = select.select(self._conn_list,
                                                            self._conn_list,
                                                            self._conn_list)
            if self._sock in readable:
                conn, address = self._sock.accept()
                print("new connection from" + str(address))
                conn.setblocking(0)
                self._conn_list.append(conn)

                msg_queues[conn] = queue.Queue()

            for sock in readable:
                if sock is self._sock:
                    continue
                else:
                    msg = sock.recv(1024)

                    if msg:

                        keys = msg_queues.keys()
                        for key in keys:
                            if key is sock:
                                continue
                            else:
                                msg_queues[key].put(msg)
                                if key not in outputs:
                                    outputs.append(key)
                    else:
                        self._conn_list.remove(sock)
                        sock.close()

            for sock in writable:
                if sock is self._sock:
                    continue
                else:
                    try:
                        msg = msg_queues[sock].get_nowait()
                    except queue.Empty:
                        pass
                        #  print(str(sock.getpeername()) + "is empty, removing "
                        #                                  + "from outputs")
                        #  self._conn_list.remove(sock)  # EXPERIMENTAL
                    else:
                        print("sending " + msg.decode() + " to "
                              + str(sock.getpeername()))
                        sock.send(msg)

            for sock in exceptional:
                print("handling exceptional condition for "
                      + sock.getpeername())
                if sock is self._sock:
                    print("exceptional condition on server socket, quitting")
                    sys.exit(1)
                else:
                    self._conn_list.remove(sock)
                    sock.close()
                    del msg_queues[sock]












