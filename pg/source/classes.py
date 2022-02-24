import random

import pygame
from settings import COLORS, RECT, SETTINGS, DIRECTION, FONT, KEYS, vec


class Snake(list):

    def __init__(self, engine):
        list.__init__(self, [(0, 1)])
        self.engine = engine
        self.direction = vec(1, 0)
        self.speed = SETTINGS.SPEED
        self.length = SETTINGS.LENGTH

        self.turn_queue = []

        self.generate_images()

    @classmethod
    def generate_images(cls):
        cls.HEAD_IMAGE = pygame.Surface((SETTINGS.TILE, SETTINGS.TILE), pygame.SRCALPHA, 32).convert_alpha()
        cls.BODY_IMAGE = pygame.Surface((SETTINGS.TILE, SETTINGS.TILE), pygame.SRCALPHA, 32).convert_alpha()

        pygame.draw.rect(cls.BODY_IMAGE, COLORS.BODY, RECT.BODY)
        pygame.draw.rect(cls.BODY_IMAGE, COLORS.PATTERN, RECT.PATTERN)

        pygame.draw.rect(cls.HEAD_IMAGE, COLORS.BODY, RECT.BODY)
        pygame.draw.rect(cls.HEAD_IMAGE, COLORS.PATTERN, RECT.LEFT_EYE)
        pygame.draw.rect(cls.HEAD_IMAGE, COLORS.PATTERN, RECT.RIGHT_EYE)

    @property
    def head(self):
        return vec(self[-1])

    def move(self):
        if self.turn_queue:
            self.direction = self.turn_queue.pop(0)

        head = self.head + self.direction

        if SETTINGS.WALLS:
            if head.x < 0 or head.x > SETTINGS.WIDTH or head.y < 1 or head.y > SETTINGS.HEIGHT:
                self.engine.running[2] = True
                return
        else:
            head.x %= SETTINGS.WIDTH
            if head.y < 1:
                head.y = SETTINGS.HEIGHT
            if head.y > SETTINGS.HEIGHT:
                head.y = 1

        self.append(tuple(head))

        if len(self) > self.length:
            del self[0]

    def turn(self, direction):
        next_direction = vec(direction)
        if self.turn_queue or self.direction != - next_direction:
            self.turn_queue.append(next_direction)
            if len(self.turn_queue) > 2:
                del self.turn_queue[0]

    def eat(self, apple):
        self.length += 1
        self.speed *= 1 - SETTINGS.ACCELERATION
        apple.repos(self)

    def render(self, display):
        for tile in self[:-1]:
            display.blit(Snake.BODY_IMAGE, vec(tile) * SETTINGS.TILE)
        head = pygame.transform.rotate(Snake.HEAD_IMAGE, self.direction.angle_to(DIRECTION.UP))
        display.blit(head, self.head * SETTINGS.TILE)


class Apple:
    FIELD = {(x, y + 1) for x in range(SETTINGS.WIDTH) for y in range(SETTINGS.HEIGHT)}
    IMAGE = None

    def __init__(self):
        self.pos = vec(0, 0)
        self.generate_images()

    @classmethod
    def generate_images(cls):
        cls.IMAGE = pygame.Surface((SETTINGS.TILE, SETTINGS.TILE), pygame.SRCALPHA, 32).convert_alpha()
        pygame.draw.rect(cls.IMAGE, COLORS.APPLE, RECT.APPLE)

    def repos(self, snake):
        empty = tuple(Apple.FIELD - set(snake))
        self.pos = vec(random.choice(empty))

    def render(self, display):
        display.blit(Apple.IMAGE, self.pos * SETTINGS.TILE)
