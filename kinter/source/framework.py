from tkinter import Tk, Canvas, BOTH
from tkinter import Tk, Canvas, BOTH
from tkinter.font import Font

from source.clock import Clock, Timer
from source.events import EventHandler
from source.game import (
    Field, Snake, Apple, Bonus, Intro, Menu, Start, Game, GameOver, NewHighScore, Paused, Settings,
    KeyConfig, HighScores, Outro
)
from source.interface import Widget, Interface, WidgetGroup, Button, WindowHeader, HeaderButton, TextLabel
from source.settings import SETTINGS, COLORS, LAYOUT
from source.state_machine import StateMachine


class Framework(Tk, StateMachine):

    def __init__(self):

        Tk.__init__(self)
        TextLabel.FONT = [Font(family=LAYOUT.FONT, size=size, weight="bold") for size in LAYOUT.FONT_SIZES]

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

        # --- INTERFACE ---------------------------------------------------------------------------------------------- #
        self.interface = Interface()

        # header #
        self.header_group = WidgetGroup(self.interface, "Header", active=True)
        self.header = WindowHeader(self.header_group, self)
        self.close_button = HeaderButton(self.header_group, LAYOUT.CLOSE_BUTTON, COLORS.RED_BUTTON)

        # menu #
        self.menu_group = WidgetGroup(self.interface, "Menu")
        self.start_group = WidgetGroup(self.interface, "Start")
        self.resume_group = WidgetGroup(self.interface, "Resume")

        self.start_button = Button(self.start_group, LAYOUT.START_BUTTON, "Play", colors=COLORS.GREEN_BUTTON,
                                   text_size=2)
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

        # start #
        self.start_game_group = WidgetGroup(self.interface, "Start game")
        self.start_game_label = TextLabel(self.start_game_group, LAYOUT.START_GAME_LABEL, "Press any key to start",
                                          text_size=0, color=COLORS.WHITE_LABEL)

        # game over #
        self.game_over_group = WidgetGroup(self.interface, "Start game")
        self.game_over_label = TextLabel(self.game_over_group, LAYOUT.GAME_OVER_LABEL, "Game over", text_size=2,
                                         color=COLORS.RED_LABEL)
        self.game_over_menu_button = Button(self.game_over_group, LAYOUT.GAME_OVER_MENU_BUTTON, "Menu")
        self.game_over_restart_button = Button(self.game_over_group, LAYOUT.GAME_OVER_RESTART_BUTTON, "Play again",
                                               colors=COLORS.GREEN_BUTTON)

        # --- STATE MACHINE ------------------------------------------------------------------------------------------ #

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
        self.state_events(self.event_handler)

        if self.close_button.pressed:
            self.running = False

    def logic(self):
        if self.loop_timer():
            self.state_logic()

    def render(self):
        self.display.delete("all")
        self.field.render_background(self.display)
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
