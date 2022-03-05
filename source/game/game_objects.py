from random import choice, randrange

from source.engine.clock import Timer
from source.engine.settings import SETTINGS, COLORS, LAYOUT
from source.engine.tools import Vector, Matrix, Rectangle, Direction


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

    def render_background(self, display):
        display.create_rectangle(*self.rect, fill=COLORS.FIELD, outline=COLORS.FIELD)

    def fade_content(self, display):
        display.create_rectangle(*self.rect, fill=COLORS.FADE, outline=COLORS.FADE, stipple='gray75')


class Snake:

    def __init__(self, field):
        self.position = self.direction = self.heading = self.stats = self.length = self.speed = None
        self.reset(field)
        self.delays = {i: self.delay(i) for i in range(SETTINGS.SPEED_MAPPING[0], SETTINGS.SPEED_MAPPING[1]+1)}

        self.turn_queue = []

    @property
    def next_position(self):
        return self.position + self.direction

    def reset(self, field):
        self.position = Vector(randrange(LAYOUT.FIELD_SIZE[0] - 8) + 4, randrange(LAYOUT.FIELD_SIZE[1] - 8) + 4)
        self.direction = choice((Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN))
        self.heading = Vector(self.direction)
        self.length = SETTINGS.STARTING_LENGTH
        self.speed = SETTINGS.STARTING_SPEED
        self.stats = {"apple": 0, "bonus": 0}

        for tile in range(self.length):
            field[self.position - self.direction * tile] = self.length - tile

    def change_direction(self):
        if self.turn_queue and (direction := self.turn_queue.pop(0)) != -self.direction:
            self.direction = direction

    def move(self):
        self.position = self.position + self.direction
        self.heading = Vector(self.direction)

    def turn(self, direction):
        self.turn_queue.append(direction)
        if len(self.turn_queue) > 2:
            del self.turn_queue[0]

    @staticmethod
    def delay(speed):
        start, end, high, low = SETTINGS.SPEED_MAPPING
        multiply = (low/high) ** (1.0/(end-start))
        return high * multiply ** (speed-start)


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
        self._animation_timer = Timer(clock, 120)
        self._lifetime_timer = Timer(clock, lifetime)
        self._active = False
        self._animation_state = True

    def update(self, framework):
        if self._lifetime_timer():
            self.deactivate(framework)
            framework.field[self.position] = 0
        if self.active and self._animation_timer():
            self._animation_state = not self._animation_state
            framework.field[self.position] = self.ID - int(self._animation_state)
        framework.bonus_timer_label.update_text(round(self._lifetime_timer.countdown(), 1))

    def update_lifetime(self, delay):
        delay = delay * (LAYOUT.FIELD_SIZE[0] + LAYOUT.FIELD_SIZE[1])
        self._lifetime_timer.set(delay)

    def activate(self, framework):
        self._active = True
        self.repos(framework.field)
        self._lifetime_timer.start()
        self._animation_timer.start()

        framework.interface.activate(framework.bonus_group)

    def deactivate(self, framework):
        self._active = False
        self._lifetime_timer.stop()
        self._animation_timer.stop()

        framework.interface.deactivate(framework.bonus_group)

    @property
    def active(self):
        return self._active

    def freeze(self):
        self._lifetime_timer.freeze()
        self._animation_timer.freeze()
