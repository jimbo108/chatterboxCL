import socket
import sys
import _thread
import curses
import curses.ascii
import signal
import copy

MAX_PORT_NUMBER = 65535
PORT = '3490'
DEFAULT_PORT = 3490
BACKLOG = 11
PORT_NUM_PRIME = 64499
DEFAULT_HOST = 'localhost'
UTF_8 = 'utf-8'


def char_buffer_to_str(buffer):
    string = ''
    for char in buffer:
        string += str(char)
    return string


class ChatClient:

    __lines_max = 10

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self._port = port
        self._host = host
        self._sock = None
        self._stdscr = curses.initscr()
        self._user_buffer = []
        self._main_buffer = []
        curses.noecho()  # Don't print characters to the screen right away
        curses.cbreak()  # React to keys before enter is pressed
        self._stdscr.keypad(True)
        signal.signal(signal.SIGINT, self.close)

    def close(self, signal=None, frame=None):
        print("in function close")
        curses.nocbreak()
        self._stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        sys.exit(0)

    def add_string_above_input(self, msg):
        # print("add_string_above_input: " + msg)
        for i, other_buffer in enumerate(self._main_buffer):
            self.clear_line(curses.LINES - 3 - i, other_buffer)
        self._main_buffer.insert(0, msg)
        if len(self._main_buffer) > ChatClient.__lines_max:
            self._main_buffer.pop()
        for i, other_buffer in enumerate(self._main_buffer):
            self.add_buffer_to_line(curses.LINES - 3 - i, other_buffer)
        self._stdscr.refresh()

    def add_buffer_to_line(self, line_num, buffer):
        # print("add_buffer_to_line: " + buffer)
        for i, ch in enumerate(buffer):
            # print("i is: " + str(i))
            self._stdscr.addstr(line_num, i, buffer[i])
        del buffer

    def clear_line(self, line_num, buffer):
        for i, ch in enumerate(buffer):
            self._stdscr.addstr(line_num, i, ' ')

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
            self.close()

    def clear_user_input_line(self, length_to_clear):
        for i in range(length_to_clear):
            self._stdscr.addstr(curses.LINES - 2, i, ' ')
        del self._user_buffer[:]
        curses.setsyx(curses.LINES - 2, 0)
        self._stdscr.refresh()

    def hold_conversation(self):
        self._sock.setblocking(0)
        _thread.start_new_thread(self.listen_conversation, ())
        while 1:
            c = self._stdscr.getch()
            if c == curses.KEY_BACKSPACE:
                if len(self._user_buffer) > 0:
                    self._stdscr.addstr(curses.LINES - 2, len(self._user_buffer)
                                        , ' ')
                    self._user_buffer.pop()
                    if len(self._user_buffer) != 0:
                        self._stdscr.addstr(curses.LINES - 2,
                                            len(self._user_buffer),
                                            self._user_buffer[len(self._user_buffer) - 1])
            elif c == curses.KEY_ENTER or c == 10 or c == 13:
                # print("hold_conversation: " + str(self._user_buffer))
                string_buffer = char_buffer_to_str(copy.copy(self._user_buffer))
                self.add_string_above_input(string_buffer)
                self._sock.send(string_buffer.encode())
                buffer_length = len(self._user_buffer)
                self.clear_user_input_line(buffer_length + 1)
            else:
                self._user_buffer.append(chr(c))
                self._stdscr.addstr(curses.LINES - 2, len(self._user_buffer), chr(c))
                self._stdscr.refresh()

    def listen_conversation(self):
        while 1:
            try:
                msg = self._sock.recv(1024)
            except socket.error:
                pass
            else:
                msg = msg.decode()
                self.add_string_above_input(msg)
