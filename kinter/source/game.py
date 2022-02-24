from settings import SETTINGS, COLORS
from random import choice
from tools import Vector, Matrix


class Field(Matrix):

    def __init__(self):
        super().__init__(SETTINGS.WIDTH, SETTINGS.HEIGHT)

    def clear(self):
        for value, at in self:
            self[at] = 0

    def update(self):
        for item, at in self:
            if item > 0:
                self[at] -= 1

    def render(self, display):

        for item, at in self:
            x, y = at
            dim = (
                x * SETTINGS.TILE + SETTINGS.GAP,
                y * SETTINGS.TILE + SETTINGS.GAP,
                (x + 1) * SETTINGS.TILE - SETTINGS.GAP,
                (y + 1) * SETTINGS.TILE - SETTINGS.GAP,
            )

            if item > 0:
                display.create_rectangle(*dim, fill=COLORS.SNAKE, outline=COLORS.FIELD)
            elif item < 0:
                display.create_rectangle(*dim, fill=COLORS.APPLE, outline=COLORS.FIELD)


class Snake:

    def __init__(self):
        self.position = Vector(0, 0)
        self.direction = Vector(1, 0)
        self.length = SETTINGS.STARTING_LENGTH

    def move(self):
        self.position += self.direction

        if self.position.x >= SETTINGS.WIDTH:
            self.position.x = 0
        if self.position.x < 0:
            self.position.x = SETTINGS.WIDTH - 1
        if self.position.y >= SETTINGS.HEIGHT:
            self.position.y = 0
        if self.position.y < 0:
            self.position.y = SETTINGS.HEIGHT - 1

    def turn(self, vector):
        if vector != -self.direction:
            self.direction = vector


class Apple:

    def __init__(self):
        self.position = Vector(0, 0)

    def repos(self, field):
        empty = [at for value, at in field if value == 0]
        self.position = Vector(*choice(empty))
        field[self.position.data] = -1
