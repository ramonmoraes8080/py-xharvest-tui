import argparse
import datetime
from tabulate import tabulate
from harvest.credentials import PersonalAccessAuthConfigCredential
from harvest.services import (
    SingleDayTimeEntries,
    CurrentWeekTimeEntries,
    MyProjectAssignmentsService,
    TodayTimeEntries,
    MonthTimeEntries,
    )
import tui

__prog__ = 'harvest'
__desc__ = 'harvest tui'
__version__ = '0.1.0'


harvest_creds = PersonalAccessAuthConfigCredential()

TABLEFMT = 'rounded_grid'


class MainWindow(tui.Window):

    color_pair = tui.COLOR_PAIR_BLACK_ON_WHITE
    status_bar = True
    borders = False

    def bind_data(self, *args, **kwargs):
        for i in range(1, 10):
            self.write(f'[{i}][0] foo', 0, i)

    def on_key_pressed(self, *args, **kwargs):
        char_code = self.get_key_pressed()
        self.logger.info(f'key code {char_code}')
        if char_code == 113:  # q
            return True
        else:
            svc = MonthTimeEntries(harvest_creds)
            svc.set_month(2023, 1)
            entries = svc.all()['time_entries']
            # entries = TodayTimeEntries(harvest_creds).all()['time_entries']
            TimeEntriesStringListWindow(entries).start()


class TimeEntriesStringListWindow(tui.StringListWindow):
 
    def bind_data(self, *args, **kwargs):
        for i, time_entry in enumerate(self.data):
            txt = f"{time_entry['id']}"
            self.logger.info(f'rendering txt = "{txt}" ({i})')
            if self.focus_idx == i:
                self.write(txt, 1, i, self.get_color_pair(self.focus_idx_color_pair))
            else:
                self.write(txt, 1, i)


class MyApp(tui.Application):

    root_window_class = MainWindow


if __name__ == '__main__':
    app = MyApp()
    app.run()

