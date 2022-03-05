from time import time


class Clock:
    """ Clock class which handles loop timing and some other time related tasks """

    def __init__(self, fps: int):
        self._fps = fps
        self._mark = 0
        self.dt = 0
        self.now = 0
        self.update()

    def update(self):
        self.now = time()
        self.dt = self.now - self._mark
        self._mark = self.now

    def leftover(self) -> float:
        """ :returns: time remaining until the current loop is ended with self._fps [frame/seconds] """
        return max(int((1 / self._fps - (time() - self._mark)) * 1000), 0)


class Timer:
    """ Timer class which gives a signal when a specified time have been passed """

    def __init__(self, clock: Clock, period: int, periodic: bool = True, running: bool = True):
        """
        Timer init
        :param clock: clock object for time reference
        :param period:
        :param periodic: if set to True, the timer automatically restarts when its expired
        :param running: enable signal. If set to False, the timer is stopped
        """
        self._clock = clock
        self._period = period / 1000
        self._mark = clock.now
        self._periodic = periodic
        self._running = running

    def __call__(self):
        """ :returns: True if the timer is expired (once per timer cycle) """

        if self._running and self._clock.now - self._period >= self._mark:
            self._mark = self._clock.now
            self._running = self._periodic
            return True
        else:
            return False

    def start(self):
        self._mark = self._clock.now
        self._running = True

    def stop(self):
        self._running = False

    def freeze(self):
        """ Freezes the timer, skipping the game cycle when it is called in """
        self._mark += self._clock.dt

    def set(self, delay):
        """ Sets a new period to the timer """
        self._period = delay / 1000

    def countdown(self) -> float:
        """ :returns: remaining time in seconds, or 0 if the timer is expired """
        return (self._mark - (self._clock.now - self._period)) * self._running
