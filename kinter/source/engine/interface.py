from abc import ABC, abstractmethod

from source.engine.settings import COLORS, LAYOUT
from source.engine.tools import Vector, Rectangle
from source.engine.events import EventHandler

from tkinter import Tk, Canvas, Event

from typing import Union, Tuple, Dict


class Group:

    _id = 0

    def __init__(self, name: str = None):
        self.name = self.id() if name is None else name
        self._widgets = []
        self._groups = []

    def __hash__(self) -> int:
        return hash(self.name)

    @classmethod
    def id(cls):
        cls._id += 1
        return str(cls._id)


class Interface:
    """ Class for managing WidgetGroup instances """

    def __init__(self):
        self._all_groups = set()
        self._active_groups = set()

    def add_group(self, *groups: Group):
        self._all_groups.update(set(groups))

    def activate(self, *groups: Group):
        """ Activates given groups exclusively """
        self._active_groups |= set(groups)

    def deactivate(self, *groups: Group):
        self._active_groups -= set(groups)

    def events(self, event_handler: EventHandler):
        for group in self._active_groups:
            group.events(event_handler)

    def render(self, display: Canvas):
        """ Renders widgets of all activated widget groups to the given surface """
        for group in self._active_groups:
            group.render(display)


class Widget(Rectangle, ABC):
    FONT = []

    def __init__(self, group: Group, dim: (int, int, int, int), align: str = "center"):
        Rectangle.__init__(self, *dim)
        group.add_widget(self)
        self.align = align

        self.base = None
        self.snap(dim[:2])

        self.hovered = False
        self.entered = False
        self.last_hovered = False

    def snap(self, pos: Union[tuple, Vector]):
        self.base = Vector(*pos)
        setattr(self, self.align, self.base)

    def events(self, event_handler: EventHandler):
        self.hovered = self.focused(event_handler.focus)
        self.entered = self.hovered and not self.last_hovered
        self.last_hovered = self.hovered

    @abstractmethod
    def render(self, display: Canvas):
        pass


class WidgetGroup(Group):

    def __init__(self, boss: Union[Interface, Group], name: str = None, active: bool = False):
        super().__init__(name)

        boss.add_group(self)
        if active and isinstance(boss, Interface):
            boss.activate(self)

    def add_group(self, group: Group):
        self._groups.append(group)

    def add_widget(self, widget: Widget):
        self._widgets.append(widget)

    def events(self, event_handler: EventHandler):
        for item in self:
            item.events(event_handler)

    def render(self, display: Canvas):
        for item in self:
            item.render(display)

    def __iter__(self):
        yield from self._widgets + self._groups


# === [ INHERITED WIDGET CLASSES ] =================================================================================== #


class TextLabel(Widget):
    FONT = []

    def __init__(
            self,
            group: WidgetGroup,
            pos: Union[Tuple[int, int], Vector],
            color: Union[str, Tuple],
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

    def text_dim(self, text: str) -> Tuple[int, int]:
        width = self.font.measure(text)
        height = self.font.metrics("linespace")
        return width, height

    def resize(self, width: int, height: int):
        super().resize(width, height)
        self.snap(self.base)

    def update_text(self, text: str):
        self.text = text
        self.resize(*self.text_dim(text))

    def render(self, display: Canvas):
        display.create_text(*self.center, text=self.text, justify="center", fill=self.color, font=self.font)

    @property
    def font(self):
        return self.FONT[self.text_size]


class Button(TextLabel):

    def __init__(
            self,
            group: WidgetGroup,
            pos: Union[Tuple[int, int], Vector],
            colors: Tuple[str, str],
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


class Switch(TextLabel):

    STATE_TEXT = ("OFF", "ON")

    def __init__(
            self,
            group: WidgetGroup,
            pos: Union[Tuple[int, int], Vector],
            colors: Tuple[Tuple[str, str], Tuple[str, str]],
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

    def relay(self):
        self.state = not self.state

    def events(self, event_handler: EventHandler):
        super().events(event_handler)
        self.pressed = self.hovered and event_handler.click[0]

        if self.pressed:
            self.relay()

        self.switched = self.state != self.last_state
        self.last_state = self.state

    def render(self, display: Canvas):
        color = self.color[self.hovered]
        w1, h1 = self.text_dim(self.text)
        w2, h2 = self.text_dim(self.STATE_TEXT[self.state])
        self.resize(w1 + w2, max(h1, h2))
        c1, c2 = self.midleft + Vector(w1 / 2, 0), self.midleft + Vector(w1 + w2 / 2, 0)
        display.create_text(c1, text=self.text, justify="center", fill=color[0], font=self.font)
        display.create_text(c2, text=self.STATE_TEXT[self.state], justify="center", fill=color[1], font=self.font)


class Slider(Widget):
    HEIGHT = 20
    THICKNESS = 5

    def __init__(
            self,
            group: WidgetGroup,
            pos: Union[Tuple[int, int], Vector],
            colors: Tuple[Tuple[str, str], Tuple[str, str]],
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

    def events(self, event_handler: EventHandler):
        super().events(event_handler)

        if self.focused(event_handler.focus) and event_handler.hold[0]:
            self.hold = True
        if not event_handler.hold[0]:
            self.hold = False

        if self.hold and (slide := min(max(event_handler.focus.x - self.left, 0), self.width)) != self.slide:
            self.slide = slide
            self.moved = True

        self.slider.left = self.slide + self.left - self.height / 2

    def render(self, display: Canvas):
        color = self.color[self.hovered or self.hold]
        display.create_rectangle(*self.rail.rect, fill=color[0], outline=color[0])
        display.create_rectangle(*self.slider.rect, fill=color[1], outline=color[1])

    @property
    def value(self):
        return self.slide / self.width

    @value.setter
    def value(self, val: float):
        slide = val * self.width
        self.slide = min(max(slide, 0), self.width)
        self.slider.left = self.slide + self.left - self.height / 2


# === [ SPECIAL WIDGETS ] ============================================================================================ #


class WindowHeader(Widget):

    def __init__(self, group: WidgetGroup, framework: Tk):
        super().__init__(group, (0, 0, LAYOUT.WIDTH, LAYOUT.TILE), align="topleft")
        self.framework = framework
        self.grab = None

    def events(self, event_handler: EventHandler):
        super().events(event_handler)

        if self.hovered and event_handler.hold[0]:
            if self.grab is None:
                self.grab = event_handler.focus
        if not event_handler.hold[0]:
            self.grab = None

        if self.grab is not None:
            window_focus = Vector(*self.framework.winfo_pointerxy()) - self.grab
            self.framework.geometry(f"+{window_focus.x}+{window_focus.y}")

    def render(self, display: Canvas):
        display.create_rectangle(*self.rect, fill=COLORS.HEADER, outline=COLORS.HEADER)


class HeaderButton(Button):

    def __init__(self, group: WidgetGroup, pos: Union[Tuple[int, int], Vector], colors: Tuple[str, str]):
        super().__init__(group, pos, colors=colors, align="topleft")
        self.resize(LAYOUT.TILE - LAYOUT.GAP * 8, LAYOUT.TILE - LAYOUT.GAP * 8)

    def render(self, display: Canvas):
        color = self.color[self.hovered]
        display.create_rectangle(*self.rect, fill=color, outline=color)


class KeyConfigSwitch(Switch):

    PLACEHOLDER = "-"

    KEYMAP = {
        '\x1b': "Escape",
        '\x11': "Control",
        '\x12': "Alt",
        '\x10': "Shift",
        '\r': "Enter",
        ' ': "Space",
        '%': "Left",
        '&': "Up",
        "'": "Right",
        '(': "Down",
    }

    def __init__(
            self,
            group: WidgetGroup,
            pos: Union[Tuple[int, int], Vector],
            colors: Tuple[str, str],
            keycode: int,
            text_size: int = 1,
            align: str = "midright",
    ):
        super().__init__(group, pos, (colors, colors), self.PLACEHOLDER, text_size, align=align)
        self.color = colors
        self.key_code = keycode
        self.set_key(keycode)

    def set_key(self, keycode):
        self.key_code = keycode
        self.update_text(self.key_name)

    @property
    def key_name(self) -> str:
        character = chr(self.key_code)
        return self.KEYMAP[character] if character in self.KEYMAP else character

    def events(self, event_handler: EventHandler):
        super().events(event_handler)

        if self.state and (keys := event_handler["any", "press"]):
            self.key_code = keys.pop()
            self.relay()

        if self.switched:
            self.update_text(self.PLACEHOLDER if self.state else self.key_name)

    def render(self, display: Canvas):
        color = self.color[self.hovered]
        display.create_text(*self.center, text=self.text, justify="center", fill=color, font=self.font)


class LabeledSlider(WidgetGroup):

    HEIGHT_SHIFT = 30

    def __init__(
            self,
            group: WidgetGroup,
            pos: Union[Tuple[int, int], Vector],
            length: int,
            colors: Tuple[Tuple[str, str], Tuple[str, str]],
            text: str,
            value: Union[int, float],
            mapping: Tuple[int, int]
    ):
        super().__init__(group)

        self.mapping = mapping
        self.moved = False
        self.hovered = False

        self._slider = Slider(self, pos, colors, length, self.inv_mapped(value))
        self._label = TextLabel(self, LAYOUT.ORIGO, colors[0][0], text, align="midleft")
        self._value_label = TextLabel(self, LAYOUT.ORIGO, colors[0][1], str(self.mapped), align="midright")

        self._label.snap((self._slider.left, pos[1] - self.HEIGHT_SHIFT))
        self._value_label.snap((self._slider.right, pos[1] - self.HEIGHT_SHIFT))

    def events(self, event_handler: EventHandler):
        super().events(event_handler)
        self._value_label.update_text(str(self.mapped))

        self.moved = self._slider.moved
        self.hovered = any(widget.hovered for widget in self._widgets)

    @property
    def mapped(self):
        return int(self._slider.value * (self.mapping[1] - self.mapping[0]) + self.mapping[0])

    def inv_mapped(self, value):
        return (value - self.mapping[0]) / (self.mapping[1] - self.mapping[0])


class StatLabel(WidgetGroup):

    def __init__(
            self,
            group: WidgetGroup,
            pos: Union[Tuple[int, int], Vector],
            width: int,
            color: Tuple[str, str, str],
    ):
        super().__init__(group)

        self.color = color

        self._label = TextLabel(self, pos, color[0], "0", align="midright")
        self._item = Rectangle(0, 0, LAYOUT.TILE - LAYOUT.GAP * 5, LAYOUT.TILE - LAYOUT.GAP * 5)
        self._item.midleft = Vector(pos) - Vector(width, 0)

        self.update_text = self._label.update_text

    def render(self, display: Canvas):
        self._label.render(display)
        display.create_rectangle(*self._item.rect, fill=self.color[1], outline=self.color[1])