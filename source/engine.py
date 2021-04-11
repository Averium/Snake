import pygame
from classes import Snake, Apple
from interface import Button, KeyTooltip
from ctypes import wintypes, windll, pointer

from settings import SETTINGS, COLORS, DIRECTION, FPS, FONT, RECT, LABEL, KEYS, vec


class Engine:

    def __init__(self):
        self.display = pygame.display.set_mode(RECT.WINDOW, pygame.NOFRAME)
        self.clock = pygame.time.Clock()
        self.timestamp = 0
        self.window_handle = pygame.display.get_wm_info()['window']

        self.head = pygame.Rect(*RECT.HEAD)
        self.exit_button = Button(self, RECT.EXIT_BUTTON, COLORS.EXIT_BUTTON)
        self.settings_button = Button(self, RECT.SETTINGS_BUTTON, COLORS.SETTINGS_BUTTON)
        self.key_tooltip = KeyTooltip(self, RECT.KEY_TOOLTIP)

        self.reset()
        self.running[1] = True

        self.click = (0, 0, 0)
        self.focus = vec(0, 0)
        self.hold = vec(0, 0)

    def reset(self):
        self.running = [True, False, False]
        
        self.snake = Snake(self)
        self.apple = Apple()
        
        self.apple.repos(self.snake)

    def events(self):
        self.click = pygame.mouse.get_pressed()
        self.focus = pygame.mouse.get_pos()
        if self.click[0]:
            if self.head.collidepoint(self.focus):
                self.drag_window()
        else:
            self.hold = vec(self.focus)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running[0] = False
            if event.type == pygame.KEYDOWN:
                if event.key == KEYS["pause"]:
                    self.running[1] = not self.running[1]
                if event.key == KEYS["restart"] and self.running[2]:
                    self.reset()
                if event.key == KEYS["exit"]:
                    self.running[0] = False

                if event.key == KEYS["up"]:
                    self.snake.turn(DIRECTION.UP)
                if event.key == KEYS["down"]:
                    self.snake.turn(DIRECTION.DOWN)
                if event.key == KEYS["left"]:
                    self.snake.turn(DIRECTION.LEFT)
                if event.key == KEYS["right"]:
                    self.snake.turn(DIRECTION.RIGHT)

            if self.exit_button.clicked():
                self.running[0] = False
            if self.settings_button.clicked():
                self.key_tooltip.active = not self.key_tooltip.active

    def logic(self):
        if not any(self.running[1:]):
            
            if self.tick(self.snake.speed):
                self.snake.move()

                if self.snake.head == self.apple.pos:
                    self.snake.eat(self.apple)

                if self.snake.head in self.snake[:-1]:
                    self.running[2] = True

    def render(self):
        self.display.fill(COLORS.BACKGROUND)
        
        self.snake.render(self.display)
        self.apple.render(self.display)

        pygame.draw.rect(self.display, COLORS.HEAD, self.head)
        self.exit_button.render(self.display)
        self.settings_button.render(self.display)

        self.write(LABEL.SCORE, COLORS.TEXT_1, RECT.SCORE_1, self.display, "midleft")
        self.write(f"{self.snake.length - SETTINGS.LENGTH}", COLORS.TEXT_2, RECT.SCORE_2, self.display, "midleft")

        if self.running[2]:
            self.write(LABEL.GAME_OVER[0], COLORS.TEXT_2, RECT.CENTER, self.display, "midbottom", True)
            self.write(LABEL.GAME_OVER[1], COLORS.TEXT_1, RECT.CENTER, self.display, "midtop", True)
        elif self.running[1]:
            self.write(LABEL.PAUSED[0], COLORS.TEXT_2, RECT.CENTER, self.display, "midbottom", True)
            self.write(LABEL.PAUSED[1], COLORS.TEXT_1, RECT.CENTER, self.display, "midtop", True)

        self.key_tooltip.render(self.display)

        pygame.display.flip()

    def loop(self):   
        while self.running[0]:
            self.clock.tick(FPS)
            self.events()
            self.logic()
            self.render()

    def tick(self, period):
        now = pygame.time.get_ticks()
        if now - period > self.timestamp:
            self.timestamp = now
            return True
        else:
            return False

    def write(self, text, color, pos=(0, 0), canvas=None, align="topleft", large=False):
        surface = FONT[large].render(text, False, color)
        rect = surface.get_rect()
        setattr(rect, align, pos)
        if canvas is not None:
            canvas.blit(surface, rect)
        return surface, rect

    def drag_window(self):
        pos = wintypes.POINT()
        windll.user32.GetCursorPos(pointer(pos))

        dx, dy = self.hold
        cx, cy = pos.x, pos.y

        x, y = int(cx - dx), int(cy - dy)
        windll.user32.MoveWindow(self.window_handle, x, y, *RECT.WINDOW, True)


if __name__ == "__main__":
    pygame.init()
    game = Engine()
    game.loop()
    pygame.quit()
