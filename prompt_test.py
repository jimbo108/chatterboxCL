import curses
import curses.ascii
import sys
import signal
import _thread
import time


class Terminal:

    __lines_max = 10

    def __init__(self):
        self._stdscr = curses.initscr()
        self._user_buffer = []
        self._others_buffer = []
        curses.noecho()  # Don't print characters to the screen right away
        curses.cbreak()  # React to keys before enter is pressed
        self._stdscr.keypad(True)
        signal.signal(signal.SIGINT, self.close)

    def close(self, signal, frame):
        print("in function close")
        curses.nocbreak()
        self._stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        sys.exit(0)

    def add_string_above_input(self, msg):
        self._others_buffer.insert(0, msg)
        if len(self._others_buffer) > Terminal.__lines_max:
            self._others_buffer.pop()
        for i, other_buffer in enumerate(self._others_buffer):
            self.add_buffer_to_line(curses.LINES - 3 - i, other_buffer)
        self._stdscr.refresh()

    def add_buffer_to_line(self, line_num, buffer):
        for i, ch in enumerate(buffer):
            self._stdscr.addstr(line_num, i, buffer[i])

    def simulate_new_msgs(self):
        i = 0
        while 1:
            i += 1
            time.sleep(5)
            self.add_string_above_input(str(i) + ":other user's message")

    def run(self):
        _thread.start_new_thread(self.simulate_new_msgs, ())
        #  docs example
        while True:
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
            else:
                self._user_buffer.append(chr(c))
                self._stdscr.addstr(curses.LINES - 2, len(self._user_buffer), chr(c))
                self._stdscr.refresh()


term = Terminal()
term.run()
