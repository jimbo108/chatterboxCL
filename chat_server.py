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
        inputs = [self._sock]
        outputs = []

        while 1:
            readable, writable, exceptional = select.select(inputs, outputs,
                                                            inputs)
            for sock in readable:

                if sock is self._sock:
                    conn, address = sock.accept()
                    print("new connection from " + str(address))
                    conn.setblocking(0)
                    inputs.append(conn)

                    msg_queues[conn] = queue.Queue()
                else:
                    msg = sock.recv(1024)
                    if msg:
                        msg_queues[sock].put(msg)
                        if sock not in outputs:
                            outputs.append(sock)
                    else:
                        print("removing " + str(sock.getpeername()) + "from"
                              + " inputs")
                        if sock in outputs:
                            outputs.remove(sock)
                        inputs.remove(sock)
                        sock.close()

                        del msg_queues[sock]

            for sock in writable:
                try:
                    msg = msg_queues[sock].get_nowait()
                except queue.Empty:
                    print(str(sock.getpeername()) + "is empty, removing from "
                                               "outputs")
                    outputs.remove(sock)
                else:
                    print("sending " + msg.decode() + " to "
                          + str(sock.getpeername()))
                    sock.send(msg)

            for sock in exceptional:
                print("handling exceptional condition for "
                      + sock.getpeername())
                inputs.remove(sock)
                if sock in outputs:
                    outputs.remove(sock)
                sock.close()

                del msg_queues[sock]


                        # pymotw uses inputs instead of single self._socket










