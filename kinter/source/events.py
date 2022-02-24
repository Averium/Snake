

class EventHandler:

    def __init__(self, framework):

        framework.bind("<Key>", self.key_press)
        framework.bind("<KeyRelease>", self.key_release)
        framework.bind("<Button>", self.mouse_press)
        framework.bind("<ButtonRelease>", self.mouse_release)

        self._key_press = set()
        self._key_hold = set()
        self._click = set()
        self._hold = set()

    def clear(self):
        self._key_press.clear()
        self._click.clear()

    def key_press(self, event):
        self._key_hold.add(event.char)
        self._key_press.add(event.char)

    def key_release(self, event):
        if event.char in self._key_hold:
            self._key_hold.remove(event.char)

    def mouse_press(self, event):
        self._click.add(event.char)
        self._hold.add(event.char)

    def mouse_release(self, event):
        if event.char in self._hold:
            self._hold.remove(event.char)

    def __getitem__(self, key_mode):
        key, mode = key_mode
        if key == "escape":
            key = "\x1b"
        if mode == "press":
            return key in self._key_press
        elif mode == "hold":
            return key in self._key_hold
