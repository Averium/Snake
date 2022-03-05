from random import random

from source.engine.settings import SETTINGS, KEYS, LAYOUT
from source.engine.state_machine import State
from source.engine.tools import Direction
from source.engine.events import EventHandler


class States:
    INTRO = "Intro"
    MENU = "Menu"
    START = "Start"
    GAME = "Game"
    GAME_OVER = "Game over"
    NEW_HIGH_SCORE = "New high score"
    PAUSED = "Paused"
    SETTINGS = "Settings"
    KEY_CONFIG = "Key config"
    HIGH_SCORES = "Leaderboard"
    OUTRO = "Outro"


class Intro(State):

    def __init__(self, state_machine):
        super().__init__(States.INTRO, state_machine)

    def check_conditions(self):
        if self.state_machine.state_timer():
            return States.MENU

    def entry_actions(self):
        self.state_machine.state_timer.start()


class Menu(State):
    """
    Start pressed -> Start
    Settings pressed -> Settings
    Key config pressed -> KeyConfig
    High scores pressed -> HighScores
    Exit pressed OR escape key pressed -> Outro
    """

    def __init__(self, state_machine):
        super().__init__(States.MENU, state_machine)

    def check_conditions(self):
        if self.state_machine.start_button.pressed:
            return States.START
        if self.state_machine.settings_button.pressed:
            return States.SETTINGS
        if self.state_machine.key_config_button.pressed:
            return States.KEY_CONFIG
        if self.state_machine.high_scores_button.pressed:
            return States.HIGH_SCORES
        if self.state_machine.event_handler[KEYS.EXIT, "press"] or self.state_machine.exit_button.pressed:
            return States.OUTRO

    def entry_actions(self):
        self.state_machine.reset()
        self.state_machine.interface.activate(self.state_machine.menu_group)
        self.state_machine.interface.activate(self.state_machine.start_group)

    def exit_actions(self):
        self.state_machine.interface.deactivate(self.state_machine.menu_group)
        self.state_machine.interface.deactivate(self.state_machine.start_group)


class Start(State):
    """
    Direction key pressed -> Game
    """

    def __init__(self, state_machine):
        super().__init__(States.START, state_machine)

    def check_conditions(self):
        if self.state_machine.event_handler["any"]:
            return States.GAME

    def entry_actions(self):
        self.state_machine.reset()
        self.state_machine.interface.activate(self.state_machine.start_game_group)

    def exit_actions(self):
        self.state_machine.interface.deactivate(self.state_machine.start_game_group)

    def render(self, display):
        self.state_machine.field.render(display, self.state_machine.snake)


class Game(State):
    """
    p key or escape pressed -> Paused
    lose condition -> GameOver
    lose condition with high score -> NewHighScore
    """

    def __init__(self, state_machine):
        super().__init__(States.GAME, state_machine)
        self._game_over = False

    def check_conditions(self):
        if self.state_machine.event_handler[KEYS.PAUSE, "press"] or \
                self.state_machine.event_handler[KEYS.EXIT, "press"]:
            return States.PAUSED
        if self._game_over:
            high_score = False
            if high_score:
                return States.NEW_HIGH_SCORE
            else:
                return States.GAME_OVER

    def entry_actions(self):
        self._game_over = False
        self.state_machine.loop_timer()

    def events(self, event_handler):
        if event_handler[KEYS.UP, "press"]:
            self.state_machine.snake.turn(Direction.UP)
        if event_handler[KEYS.DOWN, "press"]:
            self.state_machine.snake.turn(Direction.DOWN)
        if event_handler[KEYS.LEFT, "press"]:
            self.state_machine.snake.turn(Direction.LEFT)
        if event_handler[KEYS.RIGHT, "press"]:
            self.state_machine.snake.turn(Direction.RIGHT)

    def logic(self):

        self.state_machine.snake.change_direction()
        p = self.state_machine.snake.next_position

        if self.state_machine.walls and not (LAYOUT.FIELD_SIZE[0] > p.x >= 0 and LAYOUT.FIELD_SIZE[1] > p.y >= 0):
            self._game_over = True
            return

        self.state_machine.field.update()
        self.state_machine.bonus.update(self.state_machine.field)

        self.state_machine.snake.move()

        if self.state_machine.snake.position.x >= LAYOUT.FIELD_SIZE[0]:
            self.state_machine.snake.position.x = 0
        if self.state_machine.snake.position.x < 0:
            self.state_machine.snake.position.x = LAYOUT.FIELD_SIZE[0] - 1
        if self.state_machine.snake.position.y >= LAYOUT.FIELD_SIZE[1]:
            self.state_machine.snake.position.y = 0
        if self.state_machine.snake.position.y < 0:
            self.state_machine.snake.position.y = LAYOUT.FIELD_SIZE[1] - 1

        if self.state_machine.field[self.state_machine.snake.position] > 0:
            self._game_over = True

        self.state_machine.field[self.state_machine.snake.position] = self.state_machine.snake.length

        score_multiplier = SETTINGS.SPEED_MAPPING[1] - SETTINGS.SPEED_MAPPING[0] + self.state_machine.speed

        if self.state_machine.snake.position == self.state_machine.apple.position:
            self.state_machine.apple.repos(self.state_machine.field)
            self.state_machine.snake.length += 1
            self.state_machine.snake.stats["apple"] += 1
            self.state_machine.score += SETTINGS.APPLE_SCORE * score_multiplier
            self.state_machine.field[self.state_machine.snake.position] = self.state_machine.snake.length
            if not self.state_machine.bonus.active and random() < SETTINGS.BONUS_CHANCE:
                self.state_machine.bonus.activate(self.state_machine.field)
        if self.state_machine.bonus.active and self.state_machine.snake.position == self.state_machine.bonus.position:
            self.state_machine.bonus.deactivate()
            self.state_machine.score += SETTINGS.BONUS_SCORE * score_multiplier
            self.state_machine.snake.stats["bonus"] += 1

        self.state_machine.score_value_label.update_text(str(self.state_machine.score))
        self.state_machine.apple_stat_label.update_text(str(self.state_machine.snake.stats["apple"]))
        self.state_machine.bonus_stat_label.update_text(str(self.state_machine.snake.stats["bonus"]))

    def render(self, display):
        self.state_machine.field.render(display, self.state_machine.snake)


class GameOver(State):
    """
    Play again pressed -> Start
    Menu pressed -> Menu
    """

    def __init__(self, state_machine):
        super().__init__(States.GAME_OVER, state_machine)

    def check_conditions(self):
        if self.state_machine.game_over_restart_button.pressed:
            return States.START
        if self.state_machine.game_over_menu_button.pressed:
            return States.MENU

    def entry_actions(self):
        self.state_machine.interface.activate(self.state_machine.game_over_group)

    def exit_actions(self):
        self.state_machine.interface.deactivate(self.state_machine.game_over_group)

    def render(self, display):
        self.state_machine.field.render(display, self.state_machine.snake)
        self.state_machine.field.fade_content(display)


class NewHighScore(State):
    """
    Play again pressed -> Start
    Menu pressed -> Menu
    """

    def __init__(self, state_machine):
        super().__init__(States.NEW_HIGH_SCORE, state_machine)

    def check_conditions(self):
        pass

    def entry_actions(self):
        self.state_machine.interface.activate(self.state_machine.game_over_group)

    def exit_actions(self):
        self.state_machine.interface.deactivate(self.state_machine.game_over_group)

    def render(self, display):
        self.state_machine.field.render(display, self.state_machine.snake)
        self.state_machine.field.fade_content(display)


class Paused(State):
    """
    Continue pressed -> Game
    Restart pressed -> Start
    Settings pressed -> Settings
    Key config pressed -> KeyConfig
    High scores pressed -> HighScores
    Exit pressed OR escape key pressed -> Outro
    """

    def __init__(self, state_machine):
        super().__init__(States.PAUSED, state_machine)

    def check_conditions(self):
        if self.state_machine.event_handler[KEYS.PAUSE, "press"] or self.state_machine.continue_button.pressed or \
                self.state_machine.event_handler[KEYS.EXIT, "press"]:
            return States.GAME
        if self.state_machine.restart_button.pressed:
            return States.START
        if self.state_machine.settings_button.pressed:
            return States.SETTINGS
        if self.state_machine.key_config_button.pressed:
            return States.KEY_CONFIG
        if self.state_machine.high_scores_button.pressed:
            return States.HIGH_SCORES
        if self.state_machine.exit_button.pressed:
            return States.OUTRO

    def entry_actions(self):
        self.state_machine.interface.activate(self.state_machine.menu_group)
        self.state_machine.interface.activate(self.state_machine.resume_group)

    def exit_actions(self):
        self.state_machine.interface.deactivate(self.state_machine.menu_group)
        self.state_machine.interface.deactivate(self.state_machine.resume_group)

    def events(self, event_handler):
        self.state_machine.bonus.freeze()

    def render(self, display):
        self.state_machine.field.render(display, self.state_machine.snake)
        self.state_machine.field.fade_content(display)


class Settings(State):

    def __init__(self, state_machine):
        super().__init__(States.SETTINGS, state_machine)

    def check_conditions(self):
        if self.state_machine.settings_return_button.pressed:
            return self.state_machine.last_state

    def events(self, _):
        if self.state_machine.wall_switch.switched:
            SETTINGS.WALLS = self.state_machine.wall_switch.state
        if self.state_machine.starting_speed_slider.moved:
            SETTINGS.STARTING_SPEED = round(self.state_machine.starting_speed_slider.mapped)

    def entry_actions(self):
        self.state_machine.interface.activate(self.state_machine.settings_group)

    def exit_actions(self):
        self.state_machine.interface.deactivate(self.state_machine.settings_group)


class KeyConfig(State):

    def __init__(self, state_machine):
        super().__init__(States.KEY_CONFIG, state_machine)

    def check_conditions(self):
        if self.state_machine.key_config_return_button.pressed:
            return self.state_machine.last_state

    def events(self, _):
        if self.state_machine.reset_keys_button.pressed:
            for key, switch in self.state_machine.key_config_switches.items():
                switch.set_key(KEYS.DEFAULT[key])

    def entry_actions(self):
        self.state_machine.interface.activate(self.state_machine.key_config_group)

    def exit_actions(self):
        self.state_machine.interface.deactivate(self.state_machine.key_config_group)
        for key, switch in self.state_machine.key_config_switches.items():
            setattr(KEYS, key, switch.key_code)


class Leaderboard(State):

    def __init__(self, state_machine):
        super().__init__(States.HIGH_SCORES, state_machine)

    def check_conditions(self):
        if self.state_machine.high_scores_return_button.pressed:
            return self.state_machine.last_state

    def entry_actions(self):
        self.state_machine.interface.activate(self.state_machine.high_scores_group)

    def exit_actions(self):
        self.state_machine.interface.deactivate(self.state_machine.high_scores_group)


class Outro(State):
    """
    Time passed -> EXIT PROGRAM
    """

    def __init__(self, state_machine):
        super().__init__(States.OUTRO, state_machine)

    def check_conditions(self):
        pass

    def entry_actions(self):
        self.state_machine.running = False
