from abc import ABC, abstractmethod

from source.engine.settings import COLORS, LAYOUT
from source.engine.tools import Vector, Rectangle


class Interface:
    """ Class for managing WidgetGroup instances """

    def __init__(self):
        self._all_groups = set()
        self._active_groups = set()

    def add_groups(self, *groups):
        self._all_groups.update(set(groups))

    def activate(self, *groups):
        """ Activates given groups exclusively """
        self._active_groups |= set(groups)

    def deactivate(self, *groups):
        self._active_groups -= set(groups)

    def events(self, event_handler):
        for group in self._active_groups:
            for widget in group:
                widget.events(event_handler)

    def render(self, display):
        """ Renders widgets of all activated widget groups to the given surface """
        for group in self._active_groups:
            for widget in group:
                widget.render(display)


class WidgetGroup(list):

    def __init__(self, interface: Interface, name, active: bool = False):
        list.__init__(self)
        self.name = name
        interface.add_groups(self)

        if active:
            interface.activate(self)

    def __hash__(self):
        return hash(self.name)


class Widget(Rectangle, ABC):

    FONT = []

    def __init__(self, group: WidgetGroup, dim: (int, int, int, int), align: str = "center"):
        Rectangle.__init__(self, *dim)
        group.append(self)
        self.align = align

        self.base = None
        self.snap(dim[:2])

        self.hovered = False
        self.entered = False
        self.last_hovered = False

    def snap(self, pos):
        self.base = Vector(*pos)
        setattr(self, self.align, self.base)

    def events(self, event_handler):
        self.hovered = self.focused(event_handler.focus)
        self.entered = self.hovered and not self.last_hovered
        self.last_hovered = self.hovered

    @abstractmethod
    def render(self, surface):
        pass


# === [ INHERITED WIDGET CLASSES ] =================================================================================== #


class WindowHeader(Widget):

    def __init__(self, group, framework):
        super().__init__(group, (0, 0, LAYOUT.WIDTH, LAYOUT.TILE), align="topleft")
        self.framework = framework
        self.grab = None

    def events(self, event_handler):
        super().events(event_handler)

        if self.hovered and event_handler.hold[0]:
            if self.grab is None:
                self.grab = event_handler.focus
        if not event_handler.hold[0]:
            self.grab = None

        if self.grab is not None:
            window_focus = Vector(*self.framework.winfo_pointerxy()) - self.grab
            self.framework.geometry(f"+{window_focus.x}+{window_focus.y}")

    def render(self, display):
        display.create_rectangle(*self.rect, fill=COLORS.HEADER, outline=COLORS.HEADER)


class TextLabel(Widget):

    FONT = []

    def __init__(
            self,
            group: WidgetGroup,
            pos: (int, int),
            color: str,
            text: str,
            text_size: int = 1,
            align: str = "center"
    ):
        super().__init__(group, (*pos, 0, 0), align)
        self.align = align
        self.color = color
        self.text_size = text_size
        self.text = None

        if text is not None:
            self.update_text(text)

    def text_dim(self, text):
        width = self.font.measure(text)
        height = self.font.metrics("linespace")
        return width, height

    def resize(self, width, height):
        super().resize(width, height)
        self.snap(self.base)

    def update_text(self, text):
        self.text = text
        self.resize(*self.text_dim(text))

    def render(self, display):
        display.create_text(*self.center, text=self.text, justify="center", fill=self.color, font=self.font)

    @property
    def font(self):
        return self.FONT[self.text_size]


class Button(TextLabel):

    def __init__(
            self,
            group: WidgetGroup,
            pos: (int, int),
            colors: (str, str),
            text: str = None,
            text_size: int = 1,
            align: str = "center",
    ):
        super().__init__(group, pos, colors, text, text_size, align)
        self.pressed = False

    def events(self, event_handler):
        super().events(event_handler)
        self.pressed = self.hovered and event_handler.click[0]

    def render(self, display):
        color = self.color[self.hovered]
        display.create_text(*self.center, text=self.text, justify="center", fill=color, font=self.font)


class HeaderButton(Button):

    def __init__(self, group, pos, colors):
        super().__init__(group, pos, colors=colors, align="topleft")
        self.resize(LAYOUT.TILE - LAYOUT.GAP * 8, LAYOUT.TILE - LAYOUT.GAP * 8)

    def render(self, display):
        color = self.color[self.hovered]
        display.create_rectangle(*self.rect, fill=color, outline=color)


class Switch(TextLabel):

    STATE_TEXT = ("OFF", "ON")

    def __init__(
            self,
            group: WidgetGroup,
            pos: (int, int),
            colors: (str, str),
            text: str,
            text_size: int = 1,
            state: bool = False,
            align: str = "center",
    ):
        text = f"{text}: "
        super().__init__(group, pos, colors, text, text_size, align)

        self.pressed = False
        self.switched = True
        self.state = state
        self.last_state = state

    def events(self, event_handler):
        super().events(event_handler)
        self.pressed = self.hovered and event_handler.click[0]

        if self.pressed:
            self.relay()

        self.switched = self.state != self.last_state
        self.last_state = self.state

    def render(self, display):
        color = self.color[self.hovered]
        w1, h1 = self.text_dim(self.text)
        w2, h2 = self.text_dim(self.STATE_TEXT[self.state])
        self.resize(w1 + w2, max(h1, h2))
        c1, c2 = self.midleft + Vector(w1/2, 0), self.midleft + Vector(w1 + w2/2, 0)
        display.create_text(c1, text=self.text, justify="center", fill=color[0], font=self.font)
        display.create_text(c2, text=self.STATE_TEXT[self.state], justify="center", fill=color[1], font=self.font)

    def relay(self):
        self.state = not self.state


class Slider(Widget):

    HEIGHT = 20
    THICKNESS = 5

    def __init__(
            self,
            group: WidgetGroup,
            pos: (int, int),
            colors: (tuple, tuple),
            length: int,
            value: float,
            align: str = "center",
    ):
        dim = (*pos, length, self.HEIGHT)
        super().__init__(group, dim, align)

        self.rail = Rectangle(
            self.left,
            int((self.height - self.THICKNESS) / 2) + self.top,
            self.width,
            self.THICKNESS
        )

        self.slider = Rectangle(self.left, self.top, self.HEIGHT, self.HEIGHT)

        self.hold = False
        self.moved = False

        self.slide = 0
        self.value = value

        self.color = colors

    def events(self, interface):
        super().events(interface)

        if self.focused(interface.focus) and interface.hold[0]:
            self.hold = True
        if not interface.hold[0]:
            self.hold = False

        if self.hold and (slide := min(max(interface.focus.x - self.left, 0), self.width)) != self.slide:
            self.slide = slide
            self.moved = True

        self.slider.left = self.slide + self.left - self.height / 2

    def render(self, display):
        color = self.color[self.hovered or self.hold]
        display.create_rectangle(*self.rail.rect, fill=color[0], outline=color[0])
        display.create_rectangle(*self.slider.rect, fill=color[1], outline=color[1])

    @property
    def value(self):
        return self.slide / self.width

    @value.setter
    def value(self, val):
        slide = val * self.width
        self.slide = min(max(slide, 0), self.width)
        self.slider.left = self.slide + self.left - self.height / 2
