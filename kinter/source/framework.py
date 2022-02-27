from enum import Enum, auto
from tkinter import Tk, Canvas, BOTH

from source.clock import Clock, Timer
from source.events import EventHandler
from source.game import (
    Vector, Field, Snake, Apple, Bonus, Intro, Menu, Start, Game, GameOver, NewHighScore, Paused, Settings,
    KeyConfig, HighScores, Outro
)
from source.interface import Interface, WidgetGroup, Button, WindowHeader, HeaderButton
from source.settings import SETTINGS, COLORS, KEYS, LAYOUT
from source.state_machine import StateMachine
from source.tools import DIRECTION


class Framework(Tk, StateMachine):

    def __init__(self):

        Tk.__init__(self)

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

        self.loop_timer = Timer(self.clock, SETTINGS.STARTING_SPEED)
        self.state_timer = Timer(self.clock, 500, periodic=False, running=False)

        self.field = Field(LAYOUT.FIELD_POS, LAYOUT.FIELD_SIZE)
        self.snake = Snake(self.field)
        self.apple = Apple()
        self.apple.repos(self.field)
        self.bonus = Bonus(SETTINGS.STARTING_SPEED * (LAYOUT.FIELD_SIZE[0] + LAYOUT.FIELD_SIZE[1]) * 0.8, self.clock)

        self.score = 0

        # INTERFACE #
        self.interface = Interface()

        # header #
        self.header_group = WidgetGroup(self.interface, "Header", active=True)
        self.header = WindowHeader(self.header_group, self)
        self.close_button = HeaderButton(self.header_group, LAYOUT.CLOSE_BUTTON, COLORS.RED_BUTTON)

        # menu #
        self.menu_group = WidgetGroup(self.interface, "Menu")
        self.start_group = WidgetGroup(self.interface, "Start")
        self.resume_group = WidgetGroup(self.interface, "Resume")

        self.start_button = Button(self.start_group, LAYOUT.START_BUTTON, "Start", colors=COLORS.GREEN_BUTTON)
        self.continue_button = Button(self.resume_group, LAYOUT.RESUME_BUTTON, "Continue", colors=COLORS.GREEN_BUTTON)
        self.restart_button = Button(self.resume_group, LAYOUT.RESTART_BUTTON, "Restart", colors=COLORS.GREEN_BUTTON)
        self.settings_button = Button(self.menu_group, LAYOUT.SETTINGS_BUTTON, "Settings")
        self.key_config_button = Button(self.menu_group, LAYOUT.KEY_CONFIG_BUTTON, "Key config")
        self.high_scores_button = Button(self.menu_group, LAYOUT.HIGH_SCORES_BUTTON, "High scores")
        self.exit_button = Button(self.menu_group, LAYOUT.EXIT_BUTTON, "Exit", colors=COLORS.RED_BUTTON)

        # settings #
        self.settings_group = WidgetGroup(self.interface, "Settings")
        self.settings_return_button = Button(self.settings_group, LAYOUT.SETTINGS_RETURN_BUTTON, "Back",
                                             colors=COLORS.RED_BUTTON)

        # key config #
        self.key_config_group = WidgetGroup(self.interface, "Key config")
        self.key_config_return_button = Button(self.key_config_group, LAYOUT.KEY_CONFIG_RETURN_BUTTON, "Back",
                                               colors=COLORS.RED_BUTTON)

        # high scores #
        self.high_scores_group = WidgetGroup(self.interface, "High scores")
        self.high_scores_return_button = Button(self.high_scores_group, LAYOUT.HIGH_SCORES_RETURN_BUTTON, "Back",
                                                colors=COLORS.RED_BUTTON)

        StateMachine.__init__(self, Intro(self))

        self.add_state(
            Menu(self),
            Start(self),
            Game(self),
            GameOver(self),
            NewHighScore(self),
            Paused(self),
            Settings(self),
            KeyConfig(self),
            HighScores(self),
            Outro(self),
        )

        self.loop()

    def reset(self):
        self.field.clear()
        self.snake = Snake(self.field)
        self.apple.repos(self.field)

    def events(self):

        self.interface.events(self.event_handler)
        self.state_events()

        if self.event_handler[KEYS.UP, "press"]:
            self.snake.turn(DIRECTION.UP)
        if self.event_handler[KEYS.DOWN, "press"]:
            self.snake.turn(DIRECTION.DOWN)
        if self.event_handler[KEYS.LEFT, "press"]:
            self.snake.turn(DIRECTION.LEFT)
        if self.event_handler[KEYS.RIGHT, "press"]:
            self.snake.turn(DIRECTION.RIGHT)

        if self.close_button.pressed:
            self.running = False

    def logic(self):
        if self.loop_timer():
            self.state_logic()

    def render(self):
        self.display.delete("all")
        self.display.create_rectangle(*self.field.rect, fill=COLORS.FIELD, outline=COLORS.FIELD)
        self.state_render(self.display)
        self.interface.render(self.display)

    def loop(self):
        self.clock.update()
        self.update_states()

        self.events()
        if not self.paused:
            self.logic()
        self.render()

        self.event_handler.clear()

        if self.running:
            self.after(self.clock.leftover(), self.loop)
        else:
            self.destroy()
