from enum import Enum, auto
from tkinter import Tk, Canvas, BOTH

from source.clock import Clock, Timer
from source.events import EventHandler
from source.game import Vector, Field, Snake, Apple
from source.interface import Interface, WidgetGroup, Button, WindowHeader
from source.settings import SETTINGS, COLORS, KEYS, LAYOUT


class States(Enum):
    MENU = auto()
    SETTINGS = auto()
    GAME = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class DIRECTION:
    UP = Vector(0, -1)
    DOWN = Vector(0, 1)
    LEFT = Vector(-1, 0)
    RIGHT = Vector(1, 0)


class Framework(Tk):

    def __init__(self):
        Tk.__init__(self)
        # StateMachine.__init__(self)

        self.resizable(False, False)
        self.geometry(f"{LAYOUT.WIDTH}x{LAYOUT.HEIGHT}")
        self.geometry(f"+100+100")
        self.overrideredirect(True)

        self.running, self.paused = True, False

        self.clock = Clock(SETTINGS.FPS)
        self.event_handler = EventHandler(self)
        self.display = Canvas(
            self,
            width=LAYOUT.WIDTH,
            height=LAYOUT.HEIGHT,
            bg=COLORS.BACKGROUND,
            highlightthickness=0,
            bd=0,
        )
        self.display.pack(fill=BOTH, expand=True)

        self.timer = Timer(self.clock, SETTINGS.STARTING_SPEED)
        self.field = Field(LAYOUT.FIELD_POS, LAYOUT.FIELD_SIZE)
        self.snake = Snake()
        self.apple = Apple()
        self.apple.repos(self.field)

        self.interface = Interface()

        self.header_group = WidgetGroup(self.interface, "Header", active=True)
        self.header = WindowHeader(self.header_group, self)

        self.menu_group = WidgetGroup(self.interface, "Menu", active=False)
        self.start_button = Button(self.menu_group, LAYOUT.START_BUTTON, "Start")

        self.state = States.GAME

        self.loop()

    def reset(self):
        self.field.clear()
        self.snake = Snake()
        self.apple = Apple()

    def events(self):

        self.interface.events(self.event_handler)

        if self.event_handler[KEYS.UP, "press"]:
            self.snake.turn(DIRECTION.UP)
        if self.event_handler[KEYS.DOWN, "press"]:
            self.snake.turn(DIRECTION.DOWN)
        if self.event_handler[KEYS.LEFT, "press"]:
            self.snake.turn(DIRECTION.LEFT)
        if self.event_handler[KEYS.RIGHT, "press"]:
            self.snake.turn(DIRECTION.RIGHT)

        if self.event_handler[KEYS.EXIT, "press"]:
            self.running = False
        if self.event_handler[KEYS.PAUSE, "press"]:
            self.paused = not self.paused

    def logic(self):
        if self.timer.tick():
            self.field.update()
            self.snake.move()

            if self.field[self.snake.position] > 0:
                self.reset()
            else:
                self.field[self.snake.position] = self.snake.length

            if self.snake.position == self.apple.position:
                self.apple.repos(self.field)
                self.snake.length += 1

    def render(self):
        self.display.delete("all")
        self.field.render(self.display)
        self.interface.render(self.display)

    def loop(self):
        self.clock.update()

        self.events()
        if not self.paused:
            self.logic()
        self.render()

        self.event_handler.clear()

        if self.running:
            self.after(self.clock.leftover(), self.loop)
        else:
            self.destroy()
