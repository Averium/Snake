from abc import ABC, abstractmethod
from tkinter.font import Font

from source.settings import COLORS, LAYOUT
from source.tools import Vector, Rectangle


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

    def __init__(self, group: WidgetGroup, dim: (int, int, int, int)):
        Rectangle.__init__(self, *dim)
        group.append(self)

        self.hovered = False
        self.entered = False
        self.last_hovered = False

        self.font = Font(family=LAYOUT.FONT, size=LAYOUT.FONT_SIZE, weight="bold")

    @classmethod
    def text(cls, display, pos, text, color, size=24):
        display.create_text(*pos, text, fill=color, size=size, justify="center")

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
        super().__init__(group, (0, 0, LAYOUT.WIDTH, LAYOUT.TILE))
        self.framework = framework
        self.grab = None

    def events(self, event_handler):
        super().events(event_handler)

        if self.hovered and event_handler.hold[0]:
            if self.grab is None:
                self.grab = event_handler.focus
            window_focus = Vector(*self.framework.winfo_pointerxy()) - self.grab
            self.framework.geometry(f"+{window_focus.x}+{window_focus.y}")
        else:
            self.grab = None

    def render(self, display):
        display.create_rectangle(*self.rect, fill=COLORS.HEADER, outline=COLORS.HEADER)


class Label(Widget):

    def __init__(
            self,
            group: WidgetGroup,
            pos: (int, int),
            text: str,
            color: (int, int, int),
            alignment: str = "center",
    ):
        super().__init__(group, [*pos, *self.text_size(text, size=32)])
        self.pos = pos
        self.color = color
        self.alignment = alignment

    def render(self, surface):
        pass

    def update_text(self, text):
        pass


class Button(Widget):

    def __init__(self, group, pos, text: str, colors: (tuple, tuple) = COLORS.WHITE_BUTTON):
        super().__init__(group, (*pos, 0, 0))
        if text:
            width = self.font.measure(text)
            height = self.font.metrics("linespace")
            self.resize(width, height)
            self.move(-Vector(width/2, height/2))

        self.text = text
        self.pressed = False
        self.colors = colors

    def events(self, event_handler):
        super().events(event_handler)
        self.pressed = self.hovered and event_handler.click[0]

        if self.entered:
            pass  # Mixer.play("blip")

    def render(self, display):
        color = self.colors[self.hovered]
        display.create_text(*self.center, text=self.text, justify="center", fill=color, font=self.font)


class HeaderButton(Button):

    def __init__(self, group, pos, colors):
        super().__init__(group, pos, "", colors)
        self.resize(LAYOUT.TILE - LAYOUT.GAP * 8, LAYOUT.TILE - LAYOUT.GAP * 8)

    def render(self, display):
        color = self.colors[self.hovered]
        display.create_rectangle(*self.rect, fill=color, outline=color)


class Switch(Widget):

    def __init__(
            self,
            group: WidgetGroup,
            dim: (int, int, int, int),
            text: str,
            colors: (tuple, tuple),
            state: bool = False,
    ):
        on_text = f"{text}: ON"
        off_text = f"{text}: OFF"

        super().__init__(group, *dim)

        self.pressed = False
        self.switched = True
        self.state = state
        self.last_state = state
        self.colors = colors
        self.text = text

    def events(self, event_handler):
        super().events(event_handler)
        self.pressed = self.hovered and event_handler.click[0]

        if self.entered:
            pass  # Mixer.play("blip")

        if self.pressed:
            self.relay()
            pass  # Mixer.play("blip")

        self.switched = self.state != self.last_state
        self.last_state = self.state

    def render(self, surface):
        if self.state:
            surface.blit(self.hovered_on_image if self.hovered else self.passive_on_image, self)
        else:
            surface.blit(self.hovered_off_image if self.hovered else self.passive_off_image, self)

    def relay(self):
        self.state = not self.state


class Slider(Widget):
    HEIGHT = 10
    THICKNESS = 10

    def __init__(
            self,
            group: WidgetGroup,
            dim: (int, int, int, int),
            length: int,
            value: float,
            colors: (tuple, tuple, tuple),
    ):
        super().__init__(group, *dim)

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32).convert_alpha()
        self.ball_image = pg.transform.scale(pg.image.load("sprites/ball.png"), (self.height, self.height))

        slider_dim = (0, int((self.height - self.THICKNESS) / 2), self.width, self.THICKNESS)
        pygame.draw.rect(self.image, colors[0], slider_dim)

        self.hold = False
        self.slide = 0
        self.value = value

    def events(self, interface):
        if self.collidepoint(*interface.focus) and interface.hold[0]:
            self.hold = True
        if not interface.hold[0]:
            self.hold = False

        if self.hold:
            self.slide = min(max(interface.focus.x - self.left, 0), self.width)

    def render(self, surface):
        surface.blit(self.image, self)
        surface.blit(self.ball_image, (self.slide + self.left - self.height / 2, self.top))

    @property
    def value(self):
        return self.slide / self.width

    @value.setter
    def value(self, val):
        slide = val * self.width
        self.slide = min(max(slide, 0), self.width)
