from time import time


class Clock:

    def __init__(self, fps):
        self._fps = fps
        self._mark = 0
        self.dt = 0
        self.now = 0
        self.update()

    def update(self):
        self.now = time()
        self.dt = self.now - self._mark
        self._mark = self.now

    def leftover(self):
        return max(int((1/self._fps - (time() - self._mark)) * 1000), 0)


class Timer:

    def __init__(self, clock, period, periodic=True, running=True):
        self._clock = clock
        self._period = period / 1000
        self._mark = clock.now
        self._periodic = periodic
        self._running = running

    def __call__(self):
        if self._running and self._clock.now - self._period >= self._mark:
            self._mark += self._period
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
        self._mark += self._clock.dt

    def set(self, delay):
        self._period = delay / 1000
