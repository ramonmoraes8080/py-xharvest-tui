import curses
import logging
from datetime import datetime

filename = 'log.txt'
logging.basicConfig(filename=filename, filemode='a',
        format="%(asctime)s, %(msecs)d %(name)s %(levelname)s %(module)s %(filename)s:%(lineno)d %(message)s",
                    datefmt="%H:%M:%S",
                    level=logging.DEBUG)


logger = logging.getLogger()

COLOR_PAIR_BLACK_ON_WHITE = 1
COLOR_PAIR_WHITE_ON_BLACK = 2
COLOR_PAIR_WHITE_ON_GREEN = 3


def init_default_color_pairs():
    curses.init_pair(COLOR_PAIR_BLACK_ON_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(COLOR_PAIR_WHITE_ON_BLACK, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIR_WHITE_ON_GREEN, curses.COLOR_WHITE, curses.COLOR_GREEN)


class Window(object):

    color_pair = COLOR_PAIR_BLACK_ON_WHITE
    borders = False

    def __init__(self, win=None, height=0, width=0, bgn_y=0, bgn_x=0):
        self.logger = logger
        if win:
            self.win = win
        else:
            self.logger.info('creating a new window')
            if height == 0 and width == 0:
                height = curses.LINES
                width = curses.COLS
            self.win = curses.newwin(height, width, bgn_y, bgn_x)
        self.win.keypad(1)

    def render_layout(self, *args, **kwargs):
        if self.color_pair:
            self.set_background(self.color_pair)
        if self.borders:
            self.win.box('|', '-')

    def start(self, *args, **kwargs):
        win_name = self.__class__.__name__
        self.logger.info(f'starting new Window {win_name} loop')
        while True:
            self.logger.info(f'cleaning window {win_name}')
            self.win.clear()
            self.render_layout()
            self.logger.info('binding data')
            self.bind_data()
            self.logger.info(f'refreshing window {win_name}')
            self.win.refresh()
            should_quit = self.on_key_pressed()
            if should_quit:
                self.logger.info(f'quitting window {win_name}')
                break

    def get_color_pair(self, color_pair):
        return curses.color_pair(color_pair)

    def write(self, txt, x, y, *args):
        self.win.addstr(y, x, txt, *args)

    def get_key_pressed(self, *args, **kwargs):
        return self.win.getch()

    def on_key_pressed(self, *args, **kwargs):
        raise NotImplemented

    def bind_data(self, *args, **kwargs):
        raise NotImplemented

    def set_background(self, color_pair):
        self.win.bkgd(' ', curses.color_pair(color_pair))


class StatusBarWindow(Window):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.set_background(COLOR_PAIR_BLACK_ON_WHITE)

    def bind_data(self):
        self.write('Status Bar', 0, 10)

    def on_key_pressed(self, *args, **kwargs):
        pass


class ListWindow(Window):

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.info(f'list data = {data}')
        self.data = data
        self.focus_idx = 0

    def on_key_pressed(self, *args, **kwargs):
        char_code = self.get_key_pressed()
        self.logger.info(f'on_key_pressed > char_code = {char_code}')
        if char_code == 113:  # q
            return True

        self.logger.info(f'curses.KEY_UP = {curses.KEY_UP}')
        self.logger.info(f'curses.KEY_DOWN = {curses.KEY_DOWN}')
        shift_focus_fn = {
            curses.KEY_UP: self.shift_focus_up,
            curses.KEY_DOWN: self.shift_focus_down,
            }.get(char_code)
        if shift_focus_fn:
            shift_focus_fn()

    def shift_focus_down(self):
        if self.focus_idx + 1 < len(self.data):
            self.focus_idx += 1
        self.logger.info(f'self.focus_idx = {self.focus_idx}')
        # TODO add log entry saying we reached the bottom limit

    def shift_focus_up(self):
        if self.focus_idx - 1 >= 0:
            self.focus_idx -= 1
        self.logger.info(f'self.focus_idx = {self.focus_idx}')
        # TODO add log entry saying we reached the top limit


class StringListWindow(ListWindow):

    focus_idx_color_pair = COLOR_PAIR_BLACK_ON_WHITE

    def bind_data(self, *args, **kwargs):
        for i, txt in enumerate(self.data):
            self.logger.info(f'rendering txt = "{txt}" ({i})')
            if self.focus_idx == i:
                self.write(txt, 1, i, curses.color_pair(self.focus_idx_color_pair))
            else:
                self.write(txt, 1, i)


class Application(object):

    root_window_class = Window

    def __init__(self, *args, **kwargs):
        pass

    def run(self):
        curses.wrapper(self.loop)

    def loop(self, stdscr):
        init_default_color_pairs()
        self.root_window = self.root_window_class(stdscr)
        self.root_window.start()

