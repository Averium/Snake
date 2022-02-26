from source.tools import Vector


class EventHandler:

    def __init__(self, framework):

        framework.bind("<Key>", self.key_press)
        framework.bind("<KeyRelease>", self.key_release)
        framework.bind("<Button>", self.mouse_press)
        framework.bind("<ButtonRelease>", self.mouse_release)
        framework.bind("<Motion>", self.mouse_motion)

        self._key_press = set()
        self._key_hold = set()
        self.click = [0, 0, 0]
        self.hold = [0, 0, 0]

        self.focus = Vector()

    def clear(self):
        self._key_press.clear()
        self.click = [0, 0, 0]

    def key_press(self, event):
        self._key_hold.add(event.char)
        self._key_press.add(event.char)

    def key_release(self, event):
        if event.char in self._key_hold:
            self._key_hold.remove(event.char)

    def mouse_press(self, event):
        self.click[event.num-1] = 1
        self.hold[event.num-1] = 1

    def mouse_release(self, event):
        if event.num in self.hold:
            self.hold[event.num-1] = 0

    def mouse_motion(self, event):
        self.focus = Vector(event.x, event.y)

    def __getitem__(self, key_mode):
        key, mode = key_mode
        if key == "escape":
            key = "\x1b"
        if mode == "press":
            return key in self._key_press
        elif mode == "hold":
            return key in self._key_hold
