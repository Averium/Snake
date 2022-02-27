from abc import ABC
from random import choice, randrange, random

from source.settings import SETTINGS, COLORS, LAYOUT, KEYS
from source.state_machine import State
from source.tools import Vector, Matrix, Rectangle, DIRECTION
from source.clock import Timer


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

    def tile_rect(self, at, gap=1):
        x, y = at
        return (
            x * LAYOUT.TILE + LAYOUT.GAP * gap + self.left,
            y * LAYOUT.TILE + LAYOUT.GAP * gap + self.top,
            (x + 1) * LAYOUT.TILE - LAYOUT.GAP * gap + self.left,
            (y + 1) * LAYOUT.TILE - LAYOUT.GAP * gap + self.top,
        )

    def render(self, display, snake):
        for item, at in self:
            if item > 0:
                display.create_rectangle(*self.tile_rect(at), fill=COLORS.SNAKE, outline=COLORS.FIELD)
                if item == snake.length:
                    close = LAYOUT.GAP * 3.5
                    far = LAYOUT.TILE - LAYOUT.GAP * 6.5

                    left = Rectangle(0, 0, LAYOUT.GAP * 3, LAYOUT.GAP * 3)
                    right = Rectangle(0, 0, LAYOUT.GAP * 3, LAYOUT.GAP * 3)

                    if snake.heading.x < 0:
                        left.left = right.left = close
                        left.top, right.top = close, far
                    elif snake.heading.x > 0:
                        left.left = right.left = far
                        left.top, right.top = close, far

                    if snake.heading.y > 0:
                        left.top = right.top = far
                        left.left, right.left = far, close
                    elif snake.heading.y < 0:
                        left.top = right.top = close
                        left.left, right.left = far, close

                    left.move(Vector(at) * LAYOUT.TILE + self.pos)
                    right.move(Vector(at) * LAYOUT.TILE + self.pos)

                    display.create_rectangle(*left.rect, fill=COLORS.PATTERN, outline=COLORS.PATTERN)
                    display.create_rectangle(*right.rect, fill=COLORS.PATTERN, outline=COLORS.PATTERN)

                else:
                    display.create_rectangle(*self.tile_rect(at, 4), fill=COLORS.PATTERN, outline=COLORS.SNAKE)
            elif item == -1:
                display.create_rectangle(*self.tile_rect(at, 2), fill=COLORS.APPLE, outline=COLORS.FIELD)
            elif item in (-2, -3):
                color = COLORS.BONUS[item+3]
                display.create_rectangle(*self.tile_rect(at, 5+item), fill=color, outline=COLORS.FIELD)


class Snake:

    def __init__(self, field):
        self.position = Vector(randrange(LAYOUT.FIELD_SIZE[0] - 8) + 4, randrange(LAYOUT.FIELD_SIZE[1] - 8) + 4)
        self.direction = choice((DIRECTION.LEFT, DIRECTION.RIGHT, DIRECTION.UP, DIRECTION.DOWN))
        self.heading = Vector(self.direction)
        self.length = SETTINGS.STARTING_LENGTH

        for tile in range(self.length):
            field[self.position - self.direction * tile] = self.length - tile

        self.turn_queue = []

    def move(self):
        if self.turn_queue:
            self.direction = self.turn_queue.pop(0)

        self.position = self.position + self.direction
        self.heading = Vector(self.direction)

        if self.position.x >= LAYOUT.FIELD_SIZE[0]:
            self.position.x = 0
        if self.position.x < 0:
            self.position.x = LAYOUT.FIELD_SIZE[0] - 1
        if self.position.y >= LAYOUT.FIELD_SIZE[1]:
            self.position.y = 0
        if self.position.y < 0:
            self.position.y = LAYOUT.FIELD_SIZE[1] - 1

    def turn(self, direction):
        if self.turn_queue or self.direction != -direction:
            self.turn_queue.append(direction)
            if len(self.turn_queue) > 2:
                del self.turn_queue[0]


class Apple:

    ID = -1

    def __init__(self):
        self.position = Vector(0, 0)

    def repos(self, field):
        empty = [at for value, at in field if value == 0]
        self.position = Vector(choice(empty))
        field[self.position] = self.ID


class Bonus(Apple):

    ID = -2

    def __init__(self, lifetime, clock):
        super().__init__()
        self._animation_timer = Timer(clock, 200)
        self._lifetime_timer = Timer(clock, lifetime)
        self._active = False
        self._animation_state = True

    def update(self, field):
        if self._lifetime_timer():
            self.deactivate()
            field[self.position] = 0
        if self.active and self._animation_timer():
            self._animation_state = not self._animation_state
            field[self.position] = self.ID - int(self._animation_state)

    def activate(self, field):
        self._active = True
        self.repos(field)
        self._lifetime_timer.start()
        self._animation_timer.start()

    def deactivate(self):
        self._active = False
        self._lifetime_timer.stop()
        self._animation_timer.stop()

    @property
    def active(self):
        return self._active


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


class GameState(State):

    def render(self, display):
        self.state_machine.field.render(display, self.state_machine.snake)


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
        self.state_machine.interface.activate(self.state_machine.menu_group)
        self.state_machine.interface.activate(self.state_machine.start_group)

    def exit_actions(self):
        self.state_machine.interface.deactivate(self.state_machine.menu_group)
        self.state_machine.interface.deactivate(self.state_machine.start_group)


class Start(GameState):
    """
    Direction key pressed -> Game
    """

    def __init__(self, state_machine):
        super().__init__(States.START, state_machine)

    def check_conditions(self):
        if any((
            self.state_machine.event_handler[KEYS.UP, "hold"],
            self.state_machine.event_handler[KEYS.DOWN, "hold"],
            self.state_machine.event_handler[KEYS.LEFT, "hold"],
            self.state_machine.event_handler[KEYS.RIGHT, "hold"],
        )):
            return States.GAME

    def entry_actions(self):
        self.state_machine.reset()


class Game(GameState):
    """
    p key or escape pressed -> Paused
    lose condition -> GameOver
    lose condition with high score -> NewHighScore
    """

    def __init__(self, state_machine):
        super().__init__(States.GAME, state_machine)

    def check_conditions(self):
        temp = False
        if self.state_machine.event_handler[KEYS.PAUSE, "press"] or \
                self.state_machine.event_handler[KEYS.EXIT, "press"]:
            return States.PAUSED
        if temp:
            if temp:
                return States.NEW_HIGH_SCORE
            else:
                return States.GAME_OVER

    def logic(self):
        game = self.state_machine

        game.field.update()
        game.bonus.update(game.field)
        game.snake.move()

        if game.field[game.snake.position] > 0:
            game.reset()
        else:
            game.field[game.snake.position] = game.snake.length

        if game.snake.position == game.apple.position:
            game.apple.repos(game.field)
            game.snake.length += 1
            game.score += 1
            game.field[game.snake.position] = game.snake.length
            if not game.bonus.active and random() < SETTINGS.BONUS_CHANCE:
                game.bonus.activate(game.field)
        if game.bonus.active and game.snake.position == game.bonus.position:
            game.bonus.deactivate()
            game.snake.length += 1
            game.score += 5


class GameOver(GameState):
    """
    Play again pressed -> Start
    Menu pressed -> Menu
    """

    def __init__(self, state_machine):
        super().__init__(States.GAME_OVER, state_machine)

    def check_conditions(self):
        pass


class NewHighScore(GameState):
    """
    Play again pressed -> Start
    Menu pressed -> Menu
    """

    def __init__(self, state_machine):
        super().__init__(States.NEW_HIGH_SCORE, state_machine)

    def check_conditions(self):
        pass


class Paused(GameState):
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
        if self.state_machine.event_handler[KEYS.PAUSE, "press"] or self.state_machine.continue_button.pressed:
            return States.GAME
        if self.state_machine.restart_button.pressed:
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
        self.state_machine.interface.activate(self.state_machine.menu_group)
        self.state_machine.interface.activate(self.state_machine.resume_group)

    def exit_actions(self):
        self.state_machine.interface.deactivate(self.state_machine.menu_group)
        self.state_machine.interface.deactivate(self.state_machine.resume_group)


class Settings(State):

    def __init__(self, state_machine):
        super().__init__(States.SETTINGS, state_machine)

    def check_conditions(self):
        if self.state_machine.settings_return_button.pressed:
            return self.state_machine.last_state

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

    def entry_actions(self):
        self.state_machine.interface.activate(self.state_machine.key_config_group)

    def exit_actions(self):
        self.state_machine.interface.deactivate(self.state_machine.key_config_group)


class HighScores(State):

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
