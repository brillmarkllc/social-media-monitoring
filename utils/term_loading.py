from threading import Thread
from threading import Event
import time


class TermLoading():
    def __init__(self):
        self.message = ""
        self.finish_message = ""
        self.__failed = False
        self.__finished = False
        self.failed_message = ""
        self.__threadEvent = Event()
        self.__thread = Thread(target=self.__loading, daemon=True)
        self.__threadBlockEvent = Event()

    @property
    def finished(self):
        return self.__finished

    @finished.setter
    def finished(self, finished):
        if isinstance(finished, bool):
            self.__finished = finished
            if finished:
                self.__threadEvent.set()
                time.sleep(0.1)
        else:
            raise ValueError

    @property
    def failed(self):
        return self.__failed

    @failed.setter
    def failed(self, failed):
        if isinstance(failed, bool):
            self.__failed = failed
            if failed:
                self.__threadEvent.set()
                time.sleep(0.1)
        else:
            raise ValueError

    def show(self, loading_message: str, finish_message: str = '✅ Finished', failed_message='❌ Failed'):
        self.message = loading_message
        self.finish_message = finish_message
        self.failed_message = failed_message
        self.show_loading()

    def show_loading(self):
        self.finished = False
        self.failed = False
        self.__threadEvent.clear()
        if not self.__thread.is_alive():
            self.__thread.start()
        else:
            self.__threadBlockEvent.set()

    def __loading(self):
        symbols = ['⣾', '⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽']
        i = 0
        while True:
            print('')
            while not self.finished and not self.failed:
                i = (i + 1) % len(symbols)
                print('\r\033[K%s %s' % (symbols[i], self.message), flush=True, end='')
                self.__threadEvent.wait(0.1)
                self.__threadEvent.clear()
            if self.finished is True and not self.failed:
                print('\r\033[K%s' % self.finish_message, flush=True)
            else:
                print('\r\033[K%s' % self.failed_message, flush=True)
            print('')
            self.__threadBlockEvent.wait()
            self.__threadBlockEvent.clear()


if __name__ == '__main__':
    animation: TermLoading = TermLoading()
    animation.show('loading...', finish_message='Finished!✅', failed_message='Failed!❌😨😨')
    time.sleep(3)
    animation.failed = True
    # loading again
    time.sleep(1)
    animation.show_loading()
    time.sleep(3)
    animation.finished = True
    time.sleep(3)