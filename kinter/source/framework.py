import os
from tkinter import Tk, Canvas, BOTH
from enum import Enum, auto

from game import Vector, Field, Snake, Apple
from clock import Clock, Timer
from events import EventHandler
from flow import Flow
from settings import SETTINGS, COLORS, KEYS


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
        super().__init__()
        self.resizable(False, False)
        self.geometry(f"{SETTINGS.WIDTH * SETTINGS.TILE}x{SETTINGS.HEIGHT * SETTINGS.TILE}")

        self.running, self.paused = True, False

        self.flow = Flow()
        self.clock = Clock(SETTINGS.FPS)
        self.event = EventHandler(self)
        self.display = Canvas(self, width=SETTINGS.WIDTH, height=SETTINGS.HEIGHT, bg=COLORS.FIELD)
        self.display.pack(fill=BOTH, expand=True)

        self.timer = Timer(self.clock, SETTINGS.STARTING_SPEED)
        self.field = Field()
        self.snake = Snake()
        self.apple = Apple()
        self.apple.repos(self.field)

        self.interface = 0

        self.state = States.GAME

        self.loop()

    def reset(self):
        self.field.clear()
        self.snake = Snake()
        self.apple = Apple()

    def events(self):

        if self.event[KEYS.UP, "press"]:
            self.snake.turn(DIRECTION.UP)
        if self.event[KEYS.DOWN, "press"]:
            self.snake.turn(DIRECTION.DOWN)
        if self.event[KEYS.LEFT, "press"]:
            self.snake.turn(DIRECTION.LEFT)
        if self.event[KEYS.RIGHT, "press"]:
            self.snake.turn(DIRECTION.RIGHT)

        if self.event[KEYS.EXIT, "press"]:
            self.running = False
        if self.event[KEYS.PAUSE, "press"]:
            self.paused = not self.paused

    def logic(self):
        if self.timer.tick():
            self.field.update()
            self.snake.move()

            if self.field[self.snake.position.data] > 0:
                self.reset()
            else:
                self.field[self.snake.position.data] = self.snake.length

            if self.snake.position == self.apple.position:
                self.apple.repos(self.field)
                self.snake.length += 1

    def render(self):
        self.display.delete("all")
        self.field.render(self.display)

    def loop(self):
        self.clock.update()

        self.events()
        if not self.paused:
            self.logic()
        self.render()

        self.event.clear()

        if self.running:
            self.after(self.clock.leftover(), self.loop)
        else:
            self.destroy()


def main():
    framework = Framework()
    framework.mainloop()


if __name__ == "__main__":
    main()
