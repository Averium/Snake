from tkinter import Tk, Canvas, BOTH
from tkinter import Tk, Canvas, BOTH
from tkinter.font import Font

from source.engine.clock import Clock, Timer
from source.engine.events import EventHandler
from source.game.game_objects import Field, Snake, Apple, Bonus
from source.game.game_states import (
    Intro, Menu, Start, Game, GameOver, NewHighScore, Paused, Settings, KeyConfig, Leaderboard, Outro
)
from source.engine.interface import (
    Widget, Interface, WidgetGroup, Button, WindowHeader, HeaderButton, TextLabel, Switch, Slider
)
from source.engine.settings import SETTINGS, COLORS, LAYOUT
from source.engine.state_machine import StateMachine


class Framework(Tk, StateMachine):

    def __init__(self):

        Tk.__init__(self)
        TextLabel.FONT = [Font(family=LAYOUT.FONT, size=size, weight="bold") for size in LAYOUT.FONT_SIZES]
        fancy_font = Font(family=LAYOUT.FANCY_FONT, size=LAYOUT.FONT_SIZES[-1], slant="italic", underline=True)
        TextLabel.FONT.append(fancy_font)

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
        self.state_timer = Timer(self.clock, 0, periodic=False, running=False)

        self.field = Field(LAYOUT.FIELD_POS, LAYOUT.FIELD_SIZE)
        self.snake = Snake(self.field)
        self.apple = Apple()
        self.apple.repos(self.field)
        self.bonus = Bonus(self.snake.delays[5] * (LAYOUT.FIELD_SIZE[0] + LAYOUT.FIELD_SIZE[1]) * 0.8, self.clock)

        self.score = 0
        self.speed = SETTINGS.STARTING_SPEED
        self.walls = SETTINGS.WALLS

        # --- INTERFACE ---------------------------------------------------------------------------------------------- #
        self.interface = Interface()

        # header #
        self.header_group = WidgetGroup(self.interface, "Header", active=True)
        self.header = WindowHeader(self.header_group, self)
        self.close_button = HeaderButton(self.header_group, LAYOUT.CLOSE_BUTTON, COLORS.RED_BUTTON)
        self.drag_label = TextLabel(self.header_group, LAYOUT.DRAG_LABEL, COLORS.FIELD, "Click here to drag window", 0,
                                    align="midleft")

        # panel #
        self.panel_group = WidgetGroup(self.interface, "Panel", active=True)
        self.title_label = TextLabel(self.panel_group, LAYOUT.TITLE_LABEL, COLORS.GREEN_LABEL, "Snake", 4)
        self.score_label = TextLabel(self.panel_group, LAYOUT.SCORE_LABEL, COLORS.WHITE_LABEL, "Score: ", 1, "midleft")
        self.score_value_label = TextLabel(self.panel_group, LAYOUT.SCORE_VALUE_LABEL, COLORS.RED_LABEL, "0", 1,
                                           "midright")
        self.speed_label = TextLabel(self.panel_group, LAYOUT.SPEED_LABEL, COLORS.WHITE_LABEL, "Speed: ", 1, "midleft")
        self.speed_value_label = TextLabel(self.panel_group, LAYOUT.SPEED_VALUE_LABEL, COLORS.RED_LABEL,
                                           str(self.speed), 1, "midright")
        self.walls_label = TextLabel(self.panel_group, LAYOUT.WALLS_LABEL, COLORS.WHITE_LABEL, "Walls: ", 1, "midleft")
        self.walls_value_label = TextLabel(self.panel_group, LAYOUT.WALLS_VALUE_LABEL, COLORS.RED_LABEL,
                                           "ON" if self.walls else "OFF", 1, "midright")
        self.stat_label = TextLabel(self.panel_group, LAYOUT.STAT_LABEL, COLORS.GREEN_LABEL, "Statistics", 2)

        # menu #
        self.menu_group = WidgetGroup(self.interface, "Menu")
        self.start_group = WidgetGroup(self.interface, "Start")
        self.resume_group = WidgetGroup(self.interface, "Resume")

        self.start_button = Button(self.start_group, LAYOUT.START_BUTTON, COLORS.GREEN_BUTTON, "Play", 3)
        self.continue_button = Button(self.resume_group, LAYOUT.RESUME_BUTTON, COLORS.GREEN_BUTTON, "Continue")
        self.restart_button = Button(self.resume_group, LAYOUT.RESTART_BUTTON, COLORS.GREEN_BUTTON, "Restart")
        self.paused_label = TextLabel(self.resume_group, LAYOUT.PAUSED_LABEL, COLORS.GREEN_LABEL, "Paused", 3)
        self.settings_button = Button(self.menu_group, LAYOUT.SETTINGS_BUTTON, COLORS.WHITE_BUTTON, "Settings")
        self.key_config_button = Button(self.menu_group, LAYOUT.KEY_CONFIG_BUTTON, COLORS.WHITE_BUTTON, "Key config")
        self.high_scores_button = Button(self.menu_group, LAYOUT.HIGH_SCORES_BUTTON, COLORS.WHITE_BUTTON, "Leaderboard")
        self.exit_button = Button(self.menu_group, LAYOUT.EXIT_BUTTON, COLORS.RED_BUTTON, "Exit")

        # settings #
        self.settings_group = WidgetGroup(self.interface, "Settings")
        self.wall_switch = Switch(self.settings_group, LAYOUT.WALL_SWITCH, COLORS.RED_SWITCH, "Walls", 1,
                                  state=SETTINGS.WALLS, align="center")
        self.settings_return_button = Button(self.settings_group, LAYOUT.SETTINGS_RETURN_BUTTON, COLORS.RED_BUTTON,
                                             "Back")
        self.starting_speed_slider = Slider(
            self.settings_group, LAYOUT.STARTING_SPEED_SLIDER, COLORS.GREEN_SLIDER, 200,
            SETTINGS.STARTING_SPEED / (SETTINGS.SPEED_MAPPING[1] - SETTINGS.SPEED_MAPPING[0])
        )
        self.starting_speed_label = TextLabel(self.settings_group, LAYOUT.ORIGO, COLORS.WHITE_LABEL, "Speed:",
                                              align="midleft")
        self.starting_speed_value_label = TextLabel(self.settings_group, LAYOUT.ORIGO, COLORS.RED_LABEL,
                                                    str(SETTINGS.STARTING_SPEED), align="midright")

        self.starting_speed_label.snap((self.starting_speed_slider.left, LAYOUT.STARTING_SPEED_LABEL))
        self.starting_speed_value_label.snap((self.starting_speed_slider.right, LAYOUT.STARTING_SPEED_VALUE_LABEL))

        # key config #
        self.key_config_group = WidgetGroup(self.interface, "Key config")
        self.key_config_return_button = Button(self.key_config_group, LAYOUT.KEY_CONFIG_RETURN_BUTTON,
                                               COLORS.RED_BUTTON, "Back")

        # high scores #
        self.high_scores_group = WidgetGroup(self.interface, "High scores")
        self.high_scores_return_button = Button(self.high_scores_group, LAYOUT.HIGH_SCORES_RETURN_BUTTON,
                                                COLORS.RED_BUTTON, "Back")

        # start #
        self.start_game_group = WidgetGroup(self.interface, "Start game")
        self.start_game_label = TextLabel(self.start_game_group, LAYOUT.START_GAME_LABEL, COLORS.WHITE_LABEL,
                                          "Press any key to start")

        # game over #
        self.game_over_group = WidgetGroup(self.interface, "Start game")
        self.game_over_label = TextLabel(self.game_over_group, LAYOUT.GAME_OVER_LABEL, COLORS.RED_LABEL, "Game over", 3)
        self.game_over_menu_button = Button(self.game_over_group, LAYOUT.GAME_OVER_MENU_BUTTON, COLORS.WHITE_BUTTON,
                                            "Menu")
        self.game_over_restart_button = Button(self.game_over_group, LAYOUT.GAME_OVER_RESTART_BUTTON,
                                               COLORS.GREEN_BUTTON, "Play again")

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
            Leaderboard(self),
            Outro(self),
        )

        self.loop()

    def reset(self):
        self.field.clear()
        self.snake.reset(self.field)
        self.apple.repos(self.field)
        self.score = 0
        self.walls = SETTINGS.WALLS
        self.speed = SETTINGS.STARTING_SPEED
        self.loop_timer.set(self.snake.delays[self.speed])

        self.score_value_label.update_text(self.score)
        self.speed_value_label.update_text(self.speed)
        self.walls_value_label.update_text("ON" if self.walls else "OFF")

    def close(self):
        SETTINGS.save()
        self.destroy()

    def events(self):

        self.interface.events(self.event_handler)
        self.state_events(self.event_handler)

        if self.close_button.pressed:
            self.running = False

        if self.wall_switch.switched:
            SETTINGS.WALLS = self.wall_switch.state

        if self.starting_speed_slider.moved:
            start, stop, high, low = SETTINGS.SPEED_MAPPING
            speed = self.starting_speed_slider.value * (stop - start) + start
            SETTINGS.STARTING_SPEED = round(speed)
            self.starting_speed_value_label.update_text(SETTINGS.STARTING_SPEED)

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
            self.close()
