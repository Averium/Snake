

class Flow:

    def __init__(self):
        self.running = True
        self.paused = True
        self.blocked = False

    def pause(self):
        self.paused = not self.paused

    def exit(self):
        self.running = False

    def restart(self):
        self.blocked, self.paused = False, False

