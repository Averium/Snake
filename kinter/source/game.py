from abc import ABC
from random import choice

from source.settings import SETTINGS, COLORS, LAYOUT
from source.state_machine import State
from source.tools import Vector, Matrix, Rectangle


# === [ Game classes ] =============================================================================================== #

class Field(Matrix, Rectangle):

    def __init__(self, pos, dim):
        Matrix.__init__(self, *dim)
        Rectangle.__init__(self, *pos, dim[0] * LAYOUT.TILE, dim[0] * LAYOUT.TILE)

    def clear(self):
        for value, at in self:
            self[at] = 0

    def update(self):
        for item, at in self:
            if item > 0:
                self[at] -= 1

    def render(self, display):

        display.create_rectangle(*self.rect, fill=COLORS.FIELD, outline=COLORS.FIELD)

        for item, at in self:
            x, y = at

            if item > 0:

                body = (
                    x * LAYOUT.TILE + LAYOUT.GAP + self.left,
                    y * LAYOUT.TILE + LAYOUT.GAP + self.top,
                    (x + 1) * LAYOUT.TILE - LAYOUT.GAP + self.left,
                    (y + 1) * LAYOUT.TILE - LAYOUT.GAP + self.top,
                )
                pattern = (
                    x * LAYOUT.TILE + LAYOUT.GAP * 4 + self.left,
                    y * LAYOUT.TILE + LAYOUT.GAP * 4 + self.top,
                    (x + 1) * LAYOUT.TILE - LAYOUT.GAP * 4 + self.left,
                    (y + 1) * LAYOUT.TILE - LAYOUT.GAP * 4 + self.top,
                )

                display.create_rectangle(*body, fill=COLORS.SNAKE, outline=COLORS.FIELD)
                display.create_rectangle(*pattern, fill=COLORS.PATTERN, outline=COLORS.SNAKE)

            elif item < 0:

                apple = (
                    x * LAYOUT.TILE + LAYOUT.GAP * 2 + self.left,
                    y * LAYOUT.TILE + LAYOUT.GAP * 2 + self.top,
                    (x + 1) * LAYOUT.TILE - LAYOUT.GAP * 2 + self.left,
                    (y + 1) * LAYOUT.TILE - LAYOUT.GAP * 2 + self.top,
                )

                display.create_rectangle(*apple, fill=COLORS.APPLE, outline=COLORS.FIELD)


class Snake:

    def __init__(self):
        self.position = Vector(0, 0)
        self.direction = Vector(1, 0)
        self.length = SETTINGS.STARTING_LENGTH

    def move(self):
        self.position = self.position + self.direction

        if self.position.x >= LAYOUT.FIELD_SIZE[0]:
            self.position.x = 0
        if self.position.x < 0:
            self.position.x = LAYOUT.FIELD_SIZE[0] - 1
        if self.position.y >= LAYOUT.FIELD_SIZE[1]:
            self.position.y = 0
        if self.position.y < 0:
            self.position.y = LAYOUT.FIELD_SIZE[1] - 1

    def turn(self, vector):
        if vector != -self.direction:
            self.direction = vector


class Apple:

    def __init__(self):
        self.position = Vector(0, 0)

    def repos(self, field):
        empty = [at for value, at in field if value == 0]
        self.position = Vector(*choice(empty))
        field[self.position] = -1


# === [ Game states ] ================================================================================================ #

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
    HIGH_SCORES = "High scores"
    OUTRO = "Outro"


class Setting(State, ABC):
    """
    Back pressed -> Menu/Paused
    """

    def check_conditions(self):
        pass


class Intro(State):

    def __init__(self, state_machine):
        super().__init__(States.INTRO, state_machine)

    def check_conditions(self):
        """
        time passed -> Menu
        """


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
        pass


class Start(State):
    """
    Direction key pressed -> Game
    """

    def __init__(self, state_machine):
        super().__init__(States.START, state_machine)

    def check_conditions(self):
        pass


class Game(State):
    """
    p key or escape pressed -> Paused
    lose condition -> GameOver
    lose condition with high score -> NewHighScore
    """

    def __init__(self, state_machine):
        super().__init__(States.GAME, state_machine)

    def check_conditions(self):
        pass


class GameOver(State):
    """
    Play again pressed -> Start
    Menu pressed -> Menu
    """

    def __init__(self, state_machine):
        super().__init__(States.GAME_OVER, state_machine)

    def check_conditions(self):
        pass


class NewHighScore(State):
    """
    Play again pressed -> Start
    Menu pressed -> Menu
    """

    def __init__(self, state_machine):
        super().__init__(States.NEW_HIGH_SCORE, state_machine)

    def check_conditions(self):
        pass


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
        pass


class Settings(Setting):

    def __init__(self, state_machine):
        super().__init__(States.SETTINGS, state_machine)


class KeyConfig(Setting):

    def __init__(self, state_machine):
        super().__init__(States.KEY_CONFIG, state_machine)


class HighScores(Setting):

    def __init__(self, state_machine):
        super().__init__(States.HIGH_SCORES, state_machine)


class Outro(State):
    """
    Time passed -> EXIT PROGRAM
    """

    def __init__(self, state_machine):
        super().__init__(States.OUTRO, state_machine)

    def check_conditions(self):
        pass
