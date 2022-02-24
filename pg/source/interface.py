import pygame
from settings import SETTINGS, COLORS, FONT, LABEL, parser


class Widget(pygame.Rect):

    def __init__(self, engine, dim):
        super().__init__(*dim)
        self.engine = engine
        self.images = self.generate_images()

    def focused(self):
        return self.collidepoint(*self.engine.focus)

    def clicked(self):
        return self.focused() and self.engine.click[0]

    def generate_images(self):
        return None


class Button(Widget):

    def __init__(self, engine, dim, color):
        self.color = color
        super().__init__(engine, dim)

    def generate_images(self):
        base = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()

        active = base.copy()
        passive = base.copy()

        gap = SETTINGS.GAP * 2
        pygame.draw.rect(active, self.color, (gap * 2, gap * 2, self.width - gap * 4, self.height - gap * 4))
        pygame.draw.rect(passive, COLORS.BUTTON, (gap * 2, gap * 2, self.width - gap * 4, self.height - gap * 4))

        return passive, active

    def render(self, display):
        display.blit(self.images[self.focused()], self)


class KeyTooltip(pygame.Surface):

    def __init__(self, engine, pos):
        _, rect = engine.write(LABEL.KEY_TOOLTIP, COLORS.TEXT_2)
        self.width = rect.width

        super().__init__((self.width + SETTINGS.GAP * 8, (len(parser["KEYS"]) + 1) * SETTINGS.TILE))
        print(len(parser["KEYS"]))
        self.rect = self.get_rect()
        self.rect.topright = pos

        self.engine = engine
        self.active = False

        self.fill(COLORS.BUTTON)
        self.engine.write(LABEL.KEY_TOOLTIP, COLORS.TEXT_2, (SETTINGS.GAP * 4, SETTINGS.GAP * 2), self)

        for i, item in enumerate(parser["KEYS"].items()):
            name, key = item

            name, name_rect = self.engine.write(f"{name} :", COLORS.PATTERN)
            key, key_rect = self.engine.write(str(key), COLORS.TEXT_1)

            name_rect.topleft = (SETTINGS.GAP * 4, SETTINGS.GAP * 2 + (i + 1) * SETTINGS.TILE)
            key_rect.topright = (self.width, SETTINGS.GAP * 2 + (i + 1) * SETTINGS.TILE)

            self.blit(name, name_rect)
            self.blit(key, key_rect)

    def render(self, display):
        if self.active:
            display.blit(self, self.rect)
