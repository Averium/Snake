from source.engine.tools import Vector


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
        # print(f"{event.keysym} - {event.keycode}")
        self._key_hold.add(event.keycode)
        self._key_press.add(event.keycode)

    def key_release(self, event):
        if event.keycode in self._key_hold:
            self._key_hold.remove(event.keycode)

    def mouse_press(self, event):
        self.click[event.num-1] = 1
        self.hold[event.num-1] = 1

    def mouse_release(self, event):
        if event.num in self.hold:
            self.hold[event.num-1] = 0

    def mouse_motion(self, event):
        self.focus = Vector(event.x, event.y)

    def __getitem__(self, key_mode):
        if key_mode == "any":
            return self._key_hold

        key, mode = key_mode

        if key == "any":
            if mode == "press":
                return self._key_press
            elif mode == "hold":
                return self._key_hold

        if mode == "press":
            return key in self._key_press
        elif mode == "hold":
            return key in self._key_hold
